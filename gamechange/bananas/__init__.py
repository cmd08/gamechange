from flask import Blueprint, render_template, abort, redirect, current_app
from jinja2 import TemplateNotFound
import time
from json import dumps, loads

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

@bananas.route('/api/')
def api_index():
	return wrap_api_call()

@bananas.route('/api/shop')
def api_shop():
	response = {'items' : [
	{'name':'Coconut', 'cost':1, 'description': 'A coconut'},
	{'name':'Shack', 'cost': 100, 'description': 'A slightly better house'}
	]}
	return wrap_api_call(response)

@bananas.route('/api/user')
def api_user():
	response = {'username':'Joe Bloggs', 'bananas': '23'}
	return wrap_api_call(response)

def wrap_api_call(json=None):
	wrapper = {'debug': True, 'api-version': 0.001, 'hostname': 'some-hostname:8888', 'system-time-millis': int(round(time.time() * 1000))}
	if(json != None):
		wrapper['data'] = json
	return dumps(wrapper)



