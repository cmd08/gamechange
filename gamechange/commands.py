from flask.ext.script import Manager
from flask import Flask
from gamechange.models import User, db


app = Flask(__name__)
app.config.from_envvar('FLASK_CONFIG')
db.init_app(app)

manager = Manager(app)

@manager.command
def reduce_health():
	[i.reduce_health(1) for i in User.query.all()]

if __name__ == "__main__":
    manager.run()