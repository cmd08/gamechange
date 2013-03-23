
from flask import Flask, render_template, jsonify, request, make_response, session, abort
from flask.ext.sqlalchemy import SQLAlchemy
from flask_mail import Message, Mail
from re import compile
import random, string
from base64 import *

app = Flask(__name__)
app.config.from_envvar('FLASK_CONFIG')
db = SQLAlchemy(app)
mail = Mail(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120))
    last_name = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True)
    verified = db.Column(db.Boolean, default=False)
    subscribed = db.Column(db.Boolean, default=True)

    def isValid(self):
        self.error = dict()
        valid = True
        if not User.query.filter_by(email=self.email).first() == None :
            self.error['email'] = "Oops! Looks like you've already signed up!"
            valid = False
        if '@' not in self.email:
            self.error['email'] = "Please check your e-mail address is valid."
            valid = False
        if self.first_name == '':
            valid = False
            self.error['first_name'] = "Please enter your first name."
        if self.last_name == '':
            valid = False
            self.error['last_name'] = "Please enter your last name."
        if self.email == '':
            valid = False
            self.error['email'] = "Please provide an e-mail address."
        return valid


    def __init__(self, first_name, last_name, email):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        
    def __repr__(self):
        return '<User %r>' % self.email

@app.before_request
def csrf_protect():
    if request.method == "POST":
        token = session.pop('_csrf_token', None)
        if not token or token != request.form.get('_csrf_token'):
            abort(403)
        else: 
            session['_csrf_token'] = generate_csrf_token()

def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(16))
    return session['_csrf_token']

app.jinja_env.globals['csrf_token'] = generate_csrf_token 

def hash(n):
  return ((0x0000FFFF & n)<<16) + ((0xFFFF0000 & n)>>16)

def send_email_to_user(user):
    msg = Message("Welcome to Game Change!", recipients=[user.email])
    msg.body = render_template('emails/signup.txt', email_key=urlsafe_b64encode(str(hash(user.id))), first_name=user.first_name, email_address=user.email)
    msg.html = render_template('emails/signup.html', email_key=urlsafe_b64encode(str(hash(user.id))), first_name=user.first_name, email_address=user.email)
    mail.send(msg)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/signup", methods=['POST'])
def signupFormSubmit():
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    user = User(first_name,last_name,email)
    if user.isValid():
        db.session.add(user)
        db.session.commit()
        #email the user!
        send_email_to_user(user)
        return jsonify(status="200", _csrf_token=session.get('_csrf_token'))

    else:
        resp = make_response(jsonify(errors=user.error, _csrf_token=session.get('_csrf_token')), 400)
        return resp

@app.route("/email/verify/<id_hash>")
def email_verify(id_hash):
    u = User.query.get(hash(int(urlsafe_b64decode(str(id_hash)))))
    if u != None:
        u.verified = True
        db.session.commit()
    else:
        #TODO should render an error here really!
        pass
    
    return render_template('signup_verified.html', first_name=u.first_name, last_name=u.last_name, email=u.email)

@app.route("/email/unsubscribe/<email>")
def email_unsubscribe(email):
    if len(email) == 0:
        #email address empty, so return here
        pass

    results = User.query.filter_by(email=email)
    if results.count() != 1:
        #email address not found, so return here
        pass

    results.first().subscribed = False
    db.session.commit()
    return "We have unsubscribed %s from our list", email

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True, port=8001)