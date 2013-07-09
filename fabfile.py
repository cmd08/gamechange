from fabric.api import local
from os import listdir, getcwd
from os.path import isfile, join

def test():
	print "Should run some tests here really..."

def pull_production():
	local("git origin production")

def start_gunicorn():
	local("gunicorn gamechange:app -D -b 0.0.0.0:8001")

def build_less(static_url_base = "http://static.gamechange.com/"):
	less_root = join(getcwd(), "gamechange/static/less")
	css_root = join(getcwd(), "gamechange/static/css")
	less_files = [ f for f in listdir(less_root) if isfile(join(less_root,f)) and f.endswith(".less") ]
	for f in less_files:
		less_file = join(less_root, f)
		css_file = join(css_root, f)
		local("lessc "+less_file+" "+css_file+" -ru -rp=" + static_url_base)


def start_dev():
	pass

def start_production():
	pull_production()
	start_gunicorn()