from gamechange import app
from .decorators import *

@app.route('/admin')
@login_required
@admin_required
def admin_view():
	print "In admin"
	return