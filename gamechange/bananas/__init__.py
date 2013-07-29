from flask import Blueprint, render_template, abort, redirect, current_app, jsonify, session, request, Response
from jinja2 import TemplateNotFound
from collections import defaultdict
import datetime
from time import mktime
import json
import healthgraph
import time
import gamechange
from gamechange.models import User, ShopItem, Shelter

bananas = Blueprint('bananas', __name__, template_folder='templates')
app = current_app

class MyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return int(mktime(obj.timetuple()))

        return json.JSONEncoder.default(self, obj)

#routes prefixed with bananas by the app
@bananas.route('/', defaults={'page': 'index'})
@bananas.route('/<page>')
def show(page):
    try:
        return render_template('bananas/%s.html' % page)
    except TemplateNotFound:
        abort(404)

@bananas.route('/js/<page>')
def js_show(page):
    try:
        return render_template('bananas/js/%s.html' % page)
    except  TemplateNotFound:
        abort(404)

@bananas.route('/de-authorize')
def deauthorize_healthgraph_api():
    return ""

@bananas.route('/fillDB')
def fill():
    Aksat = User('Aksat', 'Shah', 'gamechangedev@gmail.com')
    Ashley = User('Ashley', 'Grealish', 'ashley@gamechange.info')
    Chris = User('Chris', 'Darby', 'chris@gamechange.info')
    Joao = User('Joao', 'Some long name', 'joao@gamechange.info')
    gamechange.db.session.add(Aksat)
    gamechange.db.session.add(Ashley)
    gamechange.db.session.add(Chris)
    gamechange.db.session.add(Joao)
    gamechange.db.session.commit()
    return "Filled trial data!"

@bananas.route('/healthgraph/authorize')
def healthgraph_authorize():

    '''catch the case where the user isn't logged in to our app first'''
    if user_id not in session:
        #log in the user!
        return wrap_api_call({'redirect': '/bananas/login'}), 403

    if session.has_key('rk_access_token'):
        '''See if the user has previously authorized Healtgraph for us and it is still valid'''
        rk_access_token = session.get('rk_access_token')
        db_user = User.query.get(session['user_id'])
        db_user.healthgraph_api_key = rk_access_token
        try:
            gamechange.db.session.commit()
        except IntegrityError:
            # if the user has somehow tried to reauthorize with the same account for the same user
            gamechange.db.session.rollback()
            if rk_access_token == User.query.get(session['user_id']).healthgraph_api_key:
                return redirect('bananas/healthgraph/welcome')

            # if the user is trying to login with an account which is authorized for another user
            session.pop('rk_access_token')
            return "Oh we cant store that in the database - the access token is not unique"
        return redirect('bananas/healthgraph/welcome')
    
    else:
        '''They have not! Let's authorize them'''
        rk_auth_mgr = healthgraph.AuthManager(app.config['HEALTHGRAPH_CLIENT_ID'], 
            app.config['HEALTHGRAPH_CLIENT_SECRET'], '/'.join((app.config['BASEURL'], 'bananas/healthgraph/login',)))
        rk_auth_uri = rk_auth_mgr.get_login_url()
        rk_button_img = rk_auth_mgr.get_login_button_url('blue', 'black', 300)
        return render_template('bananas/validate.html', rk_button_img = rk_button_img, rk_auth_uri = rk_auth_uri)

@bananas.route('/healthgraph/login')
def healthgraph_login():
    code = request.args.get('code')
    if code is not None:
        rk_auth_mgr = healthgraph.AuthManager(app.config['HEALTHGRAPH_CLIENT_ID'], app.config['HEALTHGRAPH_CLIENT_SECRET'], 
            '/'.join((app.config['BASEURL'], 'bananas/healthgraph/login',)))
        rk_access_token = rk_auth_mgr.get_access_token(code)
        session['rk_access_token'] = rk_access_token
        return redirect('bananas/healthgraph/authorize')

@bananas.route('/healthgraph/welcome')
def healthgraph_welcome():
    if 'user_id' not in session:
        return wrap_api_call({'redirect':'login'}), 403
    # try to access the rk_access_token from the database based on session['user_id'] - catch if session['user_id'] not found
    try:
        rk_access_token = User.query.get(session['user_id']).healthgraph_api_key
    except AttributeError:
        return "Attribute Error: User ID doesn't exist?"

    if rk_access_token is not None:
        # try to access healthgraph data using rk_access_token from the database - catch if access token is wrong
        # and ask for user to login again
        db_user = User.query.get(session['user_id'])
        try:
            rk_user = healthgraph.User(session=healthgraph.Session(rk_access_token))
        except ValueError:
            db_user = User.query.get(session['user_id'])
            db_user.healthgraph_api_key = None
            gamechange.db.session.commit()
            session.pop('rk_access_token')
            return redirect('/bananas/healthgraph/authorize')
        else:
            stamp = mktime(db_user.last_checked.timetuple())
            modified_since = format_date_time(stamp)
            rk_profile = rk_user.get_profile()
            rk_records = rk_user.get_records()
            pdb.set_trace()
            rk_act_iter = rk_user.get_fitness_activity_iter(modified_since=modified_since)
            rk_activities = [rk_act_iter.next() for _ in range(rk_act_iter.count())]
            response = defaultdict(list)
            if rk_activities:
                for i in range(rk_act_iter.count()):
                    if rk_activities[i].get('entry_mode') == "Web":
                        activity_id = str(rk_activities[i].get('uri')[1]).split('/')[2]
                        rk_activity = dict(activity_id = str(rk_activities[i].get('uri')[1]).split('/')[2],
                            type = rk_activities[i].get('type'), 
                            start_time = rk_activities[i].get('start_time'),
                            total_distance = rk_activities[i].get('total_distance'),
                            source = rk_activities[i].get('source'),
                            entry_mode = rk_activities[i].get('entry_mode'),
                            total_calories = rk_activities[i].get('total_calories')
                            )
                        response["activities"].append(rk_activity)
                        if HealthgraphActivity.query.filter_by(id=activity_id).first() == None:		
                            activity = HealthgraphActivity(str(rk_activities[i].get('uri')[1]).split('/')[2], 
                                rk_activities[i].get('type'),
                                rk_activities[i].get('total_calories'),
                                session['user_id'])
                            db_user.last_checked = datetime.now()
                            gamechange.db.session.add(activity)
                            try:
                                gamechange.db.session.commit()
                            except IntegrityError:
                                return "Well that activity doesn't have a unique ID?"

            return Response(json.dumps(response, cls = MyEncoder, indent = 4), mimetype='application/json')
    else:
        return redirect('/bananas/healthgraph/authorize')

@bananas.route('/healthgraph/logout')
def logout():
    session.pop('rk_access_token', None)
    return "Need to redirect to the gamechange logout page - this page may be obselete depending on work from Ashley"

@bananas.route('/api/')
def api_index():
    return wrap_api_call()
>>>>>>> Stashed changes

@bananas.route('/api/users', methods = ['GET'])
def api_users():
    json_list = [i.serialize for i in User.query.all()]
    return wrap_api_call(json_list)

@bananas.route('/api/')
def api_index():
    return wrap_api_call()

@bananas.route('/api/shop', methods = ['GET'])
def api_shop_get():
    response = {'items' : [i.serialize for i in ShopItem.query.all()]}
    # {'name':'Coconut', 'cost':1, 'description': 'A coconut'},
    # {'name':'Shack', 'cost': 100, 'description': 'A slightly better house'}
    # ]}
    return wrap_api_call(response)

@bananas.route('/api/shop', methods = ['POST'])
def api_shop_post():
    name = request.form['name']
    description = request.form['description']
    type = request.form['type']
    if type == 'shelter':
        level = request.form['level']
        image_url = request.form['image_url']
        storage_space = request.form['storage_space']
        food_decay_rate_multiplier = request.form['food_decay_rate_multiplier']
        item = Shelter(name, description, level, image_url, storage_space, food_decay_rate_multiplier)
        resp = item.serialize   
    else :
        item = ShopItem(name, description)
        resp = item.serialize

    gamechange.db.session.add(item)
    gamechange.db.session.commit()
    return wrap_api_call(resp)

@bananas.route('/api/user',  methods = ['GET'])
def api_user_get():
    if "username" not in session:
        response = {'error': 'No logged in user'}
        return wrap_api_call(response), 403

    response = {'username':session['username'], 'bananas': session['bananas']}
    return wrap_api_call(response)

@bananas.route('/api/user/login', methods = ['POST'])
def api_user_logi_post():
    username = request.form['username']
    password = request.form['password']
    #Do some logic here to log the user in!
    session['username'] = username
    session['bananas'] = 0
    response = {'username': username, 'bananas': session['bananas']}
    return wrap_api_call(response)

#post doesn't work yet! Returns 403!
@bananas.route('/api/user', methods = ['POST'])
def api_user_post():
    # username = request.form['username']
    # response = {'username':username}
    response = "lol"
    return wrap_api_call(response)

def wrap_api_call(json=None):
    wrapper = {'_csrf_token': gamechange.generate_csrf_token(), 'api_version': 0.1, 'hostname': app.config['SERVER_NAME'], 'system_time_millis': int(round(time.time() * 1000))}
    if(app.config['DEBUG']):
    	wrapper['debug'] = True
    if(app.config['TESTING']):
    	wrapper['testing'] = True
    if(json != None):
        wrapper['data'] = json

    return jsonify(wrapper)
