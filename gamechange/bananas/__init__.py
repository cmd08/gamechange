from flask import Blueprint, render_template, abort, redirect, current_app, jsonify, sessions, request
from jinja2 import TemplateNotFound
import time
import gamechange
from gamechange.models import User, ShopItem

bananas = Blueprint('bananas', __name__, template_folder='templates')
app = current_app

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

@bananas.route('/healthgraph/authorize')
def healthgraph_authorize():
    pass

@bananas.route('/login')
def login():
    print ""

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
	resp = {'name': name, 'description': description}
	item = ShopItem(name, description)
	gamechange.db.session.add(item)
	gamechange.db.session.commit()
	return wrap_api_call(resp)

@bananas.route('/api/user',  methods = ['GET'])
def api_user_get():
	response = {'username':'Joe Bloggs', 'bananas': '23'}
	return wrap_api_call(response)

#post doesn't work yet! Returns 403!
@bananas.route('/api/user', methods = ['POST'])
def api_user_post():
	# username = request.form['username']
	# response = {'username':username}
	response = "lol"
	return wrap_api_call(response)


def wrap_api_call(json=None):
	wrapper = {'_csrf_token': gamechange.generate_csrf_token(), 'debug': True, 'api-version': 0.1, 'hostname': app.config['SERVER_NAME'], 'system-time-millis': int(round(time.time() * 1000))}
	if(json != None):
		wrapper['data'] = json
	return jsonify(wrapper)
