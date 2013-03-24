from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound

bananas = Blueprint('bananas', __name__, template_folder='templates')

#routes prefixed with bananas by the app
@bananas.route('/', defaults={'page': 'index'})
@bananas.route('/<page>')
def show(page):
    try:
        return render_template('bananas/%s.html' % page)
    except TemplateNotFound:
        abort(404)