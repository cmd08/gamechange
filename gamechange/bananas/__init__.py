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


conf = {'baseurl': 'http://127.0.0.1:8000'}

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

@bananas.route('/healthgraph/authorize')
def authorize():
	sess = request.environ['beaker.session']
	if sess.has_key('rk_access_token'):
		return redirect('bananas/healthgraph/welcome')
	else:
		rk_auth_mgr = healthgraph.AuthManager(app.config['HEALTHGRAPH_CLIENT_ID'], 
			app.config['HEALTHGRAPH_CLIENT_SECRET'], '/'.join(('http://127.0.0.1:8001', 'bananas/healthgraph/login',)))
		rk_auth_uri = rk_auth_mgr.get_login_url()
		rk_button_img = rk_auth_mgr.get_login_button_url('blue', 'black', 300)
		return render_template('bananas/validate.html', rk_button_img = rk_button_img, rk_auth_uri = rk_auth_uri)

@bananas.route('/healthgraph/login')
def login():
	sess = request.environ['beaker.session']
	code = request.args.get('code')
	if code is not None:
		rk_auth_mgr = healthgraph.AuthManager(app.config['HEALTHGRAPH_CLIENT_ID'], app.config['HEALTHGRAPH_CLIENT_SECRET'], 
			'/'.join(('http://127.0.0.1:8001', 'bananas/healthgraph/login',)))
		access_token = rk_auth_mgr.get_access_token(code)
		sess['rk_access_token'] = access_token
		sess.save()
		return redirect('bananas/healthgraph/welcome')

@bananas.route('/healthgraph/welcome')
def welcome():
	sess = request.environ['beaker.session']
	access_token = sess.get('rk_access_token')
	if access_token is not None:
		user = healthgraph.User(session=healthgraph.Session(access_token))
		profile = user.get_profile()
		records = user.get_records()
		act_iter = user.get_fitness_activity_iter()
		activities = [act_iter.next() for _ in range(act_iter.count())]

		response = defaultdict(list)
		for i in range(act_iter.count()):
			if activities[i].get('entry_mode') == "Web":
				activity = dict(activity_id = str(activities[i].get('uri')[1]).split('/')[2],
					type = activities[i].get('type'), 
					start_time = activities[i].get('start_time'),
					total_distance = activities[i].get('total_distance'),
					source = activities[i].get('source'),
					entry_mode = activities[i].get('entry_mode'),
					total_calories = activities[i].get('total_calories')
					)
				response["activities"].append(activity)

		return Response(json.dumps(response, cls = MyEncoder, indent = 4), mimetype='application/json')

		# return render_template('bananas/welcome.html', 
		# 	profile=profile, 
		# 	activities=activities, 
		# 	records=records.get_totals(),
		#	response=response # interprets this as string when in html jinja2 but activities works fine?
		# 	)
	else:
		return redirect('/')

@bananas.route('/healthgraph/logout')
def logout():
    sess = request.environ['beaker.session']
    sess.delete()
    return redirect('bananas/healthgraph/authorize')

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
