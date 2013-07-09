from flask import Blueprint, render_template, abort, redirect, current_app
from jinja2 import TemplateNotFound

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

