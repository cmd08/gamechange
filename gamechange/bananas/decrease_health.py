#!../../bin/python
from flask import Blueprint, render_template, abort, redirect, current_app, jsonify, session, request, Response
from jinja2 import TemplateNotFound
from collections import defaultdict
import datetime
from time import mktime
import json
import healthgraph
import time
import gamechange
from gamechange.models import User, ShopItem, UserShopItem, Shelter, db, HealthgraphActivity
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from wsgiref.handlers import format_date_time
from sqlalchemy import func
from gamechange.bananas import bananas

bananas = Blueprint('bananas', __name__, template_folder='templates')
app = current_app
# app = Flask(__name__)
# app = current_app
# db.init_app(app)

[i.reduce_health(1) for i in User.query.all()]