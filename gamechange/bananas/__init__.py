from flask import Blueprint, render_template, abort, redirect, current_app, jsonify
from jinja2 import TemplateNotFound
import healthgraph

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

@bananas.route('/de-authorize')
def deauthorize_healthgraph_api():
    return ""

@bananas.route('/healthgraph/authorize')
def healthgraph_authorize():
    pass

@bananas.route('/login')
def login():
    print ""

@bananas.route('/healthgraph/test')
def healthgraph_test():
	print ""

def index():
    sess = request.environ['beaker.session']
    if sess.has_key('rk_access_token'):
        bottle.redirect('healthgraph/test')
    else:
        rk_auth_mgr = healthgraph.AuthManager(conf['client_id'], conf['client_secret'], 
                                          '/'.join((conf['baseurl'], 'login',)))
        rk_auth_uri = rk_auth_mgr.get_login_url()
        rk_button_img = rk_auth_mgr.get_login_button_url('blue', 'black', 300)
        return bottle.template('index.html', {'rk_button_img': rk_button_img,
                                              'rk_auth_uri': rk_auth_uri,})
	# return jsonify()