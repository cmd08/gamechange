from flask import Blueprint, render_template, abort, redirect, current_app, jsonify, request, session
from jinja2 import TemplateNotFound
import healthgraph
import time

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
	print code
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
		# print user
		# fitnessactivities = healthgraph.FitnessActivityIter(resource='/fitnessActivities', session=healthgraph.Session(access_token))
		# print act_iter
		# print jsonify(user)
		activities = [act_iter.next() for _ in range(act_iter.count())]
		# print jsonify(activities)
		# return jsonify (fitnessactivities[1])
		# return jsonify (activities)
		# return jsonify(user)
		return render_template('bananas/welcome.html', 
			profile=profile, 
			activities=activities, 
			records=records.get_totals())
	else:
		return redirect('/')

@bananas.route('/healthgraph/logout')
def logout():
    sess = request.environ['beaker.session']
    sess.delete()
    return redirect('bananas/healthgraph/authorize')

@bananas.route('/api/')
def api_index():
	return wrap_api_call()

@bananas.route('/api/shop', methods = ['GET'])
def api_shop_get():
	response = {'items' : [
	{'name':'Coconut', 'cost':1, 'description': 'A coconut'},
	{'name':'Shack', 'cost': 100, 'description': 'A slightly better house'}
	]}
	return wrap_api_call(response)

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
	wrapper = {'debug': True, 'api-version': 0.1, 'hostname': app.config['SERVER_NAME'], 'system-time-millis': int(round(time.time() * 1000))}
	if(json != None):
		wrapper['data'] = json
	return jsonify(wrapper)
