from flask import render_template, abort
from jinja2 import TemplateNotFound
from gamechange import app

#error handling!
#@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(403)
def page_not_found(e):
    return render_template('errors/403.html'), 403

@app.errorhandler(500)
def page_not_found(e):
    return render_template('errors/500.html'), 500

@app.errorhandler(502)
def page_not_found(e):
    return render_template('errors/502.html'), 502

@app.errorhandler(503)
def page_not_found(e):
    return render_template('errors/503.html'), 503

@app.route('/error/<e>/')
def error_page_test(e):
    try:
    	print 'errors/%s.html' % e
        return render_template('errors/%s.html' % e), e
    except TemplateNotFound:
        abort(404)
