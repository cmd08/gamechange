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


@bananas.route('/fillDB')
def fill():
    if "user_id" in session:
        session.pop("user_id")

    Aksat = User('Aksat','Aksat', 'Shah', 'gamechangedev@gmail.com')
    Ashley = User('Ashley', 'Ashley', 'Grealish', 'ashley@gamechange.info')
    Chris = User('Chris', 'Chris', 'Darby', 'chris@gamechange.info')
    Joao = User('Joao', 'Joao', 'Some long name', 'joao@gamechange.info')
    Aksat.set_password('123')
    Ashley.set_password('123')
    Chris.set_password('123')
    Joao.set_password('123')
    gamechange.db.session.add(Aksat)
    gamechange.db.session.add(Ashley)
    gamechange.db.session.add(Chris)
    gamechange.db.session.add(Joao)
    gamechange.db.session.commit()
    return "Filled trial data!"

@bananas.route('/api/healthgraph/authorize')
def healthgraph_authorize():

    '''catch the case where the user isn't logged in to our app first'''
    if 'user_id' not in session:
        #log in the user!
        return wrap_api_call({'redirect': '/api/healthgraph/login'}), 403

    if session.has_key('rk_access_token'):
        '''See if the user has previously authorized Healtgraph for us and it is still valid'''
        rk_access_token = session.get('rk_access_token')
        db_user = User.query.get(session['user_id'])
        db_user.healthgraph_api_key = rk_access_token
        try:
            gamechange.db.session.commit()
        except IntegrityError:
            # if the user has somehow tried to reauthorize with the same account for the same user
            gamechange.db.session.rollback()
            if rk_access_token == User.query.get(session['user_id']).healthgraph_api_key:
                return redirect('bananas/api/healthgraph')

            # if the user is trying to login with an account which is authorized for another user
            session.pop('rk_access_token')
            return "Oh we cant store that in the database - the access token is not unique"
        session.pop('rk_access_token', None)
        return redirect('bananas/#/banana_run')
    
    else:
        '''They have not! Let's authorize them'''
        rk_auth_mgr = healthgraph.AuthManager(app.config['HEALTHGRAPH_CLIENT_ID'], 
            app.config['HEALTHGRAPH_CLIENT_SECRET'], '/'.join((app.config['BASEURL'], 'bananas/api/healthgraph/login',)))
        rk_auth_uri = rk_auth_mgr.get_login_url()
        rk_button_img = rk_auth_mgr.get_login_button_url('blue', 'black', 300)
        return render_template('bananas/validate.html', rk_button_img = rk_button_img, rk_auth_uri = rk_auth_uri)

@bananas.route('/api/healthgraph/login')
def healthgraph_login():
    code = request.args.get('code')
    if code is not None:
        rk_auth_mgr = healthgraph.AuthManager(app.config['HEALTHGRAPH_CLIENT_ID'], app.config['HEALTHGRAPH_CLIENT_SECRET'], 
            '/'.join((app.config['BASEURL'], 'bananas/api/healthgraph/login',)))
        rk_access_token = rk_auth_mgr.get_access_token(code)
        session['rk_access_token'] = rk_access_token
        return redirect('bananas/api/healthgraph/authorize')
    else:
        return wrap_api_call({'error':'code is required'}), 400

@bananas.route('/api/healthgraph', methods=['GET'])
def healthgraph_get():
    if 'user_id' not in session:
        return wrap_api_call({'redirect':'login'}), 403
    # try to access the rk_access_token from the database based on session['user_id'] - catch if session['user_id'] not found
    try:
        rk_access_token = User.query.get(session['user_id']).healthgraph_api_key
    except AttributeError:
        return wrap_api_call({'error':'User ID doesn\'t exist in database'}), 400

    if rk_access_token is not None:
        # try to access healthgraph data using rk_access_token from the database - catch if access token is wrong
        # and ask for user to login again
        db_user = User.query.get(session['user_id'])
        try:
            rk_user = healthgraph.User(session=healthgraph.Session(rk_access_token))
        except ValueError:
            db_user = User.query.get(session['user_id'])
            db_user.healthgraph_api_key = None
            gamechange.db.session.commit()
            session.pop('rk_access_token')
            return wrap_api_call({'error':'HealthGraph not authorized','redirect':'/api/healthgraph/authorize'}), 403
        else:
            # get activity details since the last checked time
            stamp = mktime(db_user.last_checked.timetuple())
            modified_since = format_date_time(stamp)
            rk_act_iter = rk_user.get_fitness_activity_iter(modified_since=modified_since)
            rk_activities = [rk_act_iter.next() for _ in range(rk_act_iter.count())]
            if rk_activities:
                json_list = []
                for i in range(rk_act_iter.count()):
                    if rk_activities[i].get('entry_mode') == "Web":
                        activity_id = str(rk_activities[i].get('uri')[1]).split('/')[2]
                        activity_type = rk_activities[i].get('type')
                        start_time = rk_activities[i].get('start_time')
                        calories = rk_activities[i].get('total_calories')

                        # restructure in to dict for JSON response
                        rk_activity = dict(id = activity_id,
                            activity_type = activity_type,
                            calories = calories,
                            user = session['user_id']
                            )
                        json_list.append(rk_activity)
                        # If the activity is not in the database then add it
                        if HealthgraphActivity.query.filter_by(id=activity_id).first() == None:		
                            activity = HealthgraphActivity(activity_id, 
                                activity_type,
                                calories,
                                session['user_id'])
                            db_user.last_checked = datetime.now()
                            gamechange.db.session.add(activity)
                            try:
                                gamechange.db.session.commit()
                            except IntegrityError:
                                return wrap_api_call({"error" : "activity id not unique"}), 400

                return wrap_api_call(json_list)
            else:
                json_list = [i.serialize for i in HealthgraphActivity.query.filter_by(user=session['user_id']).all()]
                return wrap_api_call(json_list)
    else:
        return wrap_api_call({'error':'HealthGraph not authorized', 'redirect':'/api/healthgraph/authorize'}), 403

@bananas.route('/api/healthgraph/logout')
def logout():
    session.pop('rk_access_token', None)
    return "Need to redirect to the gamechange logout page - this page may be obselete depending on work from Ashley"


@bananas.route('/api/')
def api_index():
    return wrap_api_call()

@bananas.route('/api/users', methods = ['GET'])
def api_users():
    json_list = [i.serialize for i in User.query.all()]
    return wrap_api_call(json_list)

@bananas.route('/api/shop', methods = ['GET'])
def api_shop_get():
    response = {'items' : [i.serialize for i in ShopItem.query.all()]}
    # {'name':'Coconut', 'cost':1, 'description': 'A coconut'},
    # {'name':'Shack', 'cost': 100, 'description': 'A slightly better house'}
    # ]}
    return wrap_api_call(response)

@bananas.route('/api/shop', methods = ['POST'])
def api_shop_post():
    name = request.form['name']
    description = request.form['description']
    type = request.form['type']
    cost = request.form['cost']
    image_url = request.form['image_url']

    if type == 'shelter':
        level = request.form['level']
        storage_space = request.form['storage_space']
        food_decay_rate_multiplier = request.form['food_decay_rate_multiplier']
        item = Shelter(name, cost, description, level, image_url, storage_space, food_decay_rate_multiplier)
        resp = item.serialize   
    elif type == 'supply':
        health_points = request.form['health_points']
        shelf_life = request.form['shelf_life']
        size = request.form['size']
        item = Supplies(name, cost, description, image_url, health_points, shelf_life, size)
        resp = item.serialize
    else:
        item = ShopItem(name, cost, description)
        resp = item.serialize

    gamechange.db.session.add(item)
    gamechange.db.session.commit()
    return wrap_api_call(resp)

@bananas.route('/api/shop/<item_id>/buy', methods = ['POST'])
def api_shop_buy_item(item_id):
    item = ShopItem.query.get(item_id)
    me = User.query.get(int(session['user_id']))
    try:
        me.add_to_inventory(item)
    except ValueError:
        return wrap_api_call({"error": "You have insufficient bananas"}), 400
    
    db.session.commit()
    return wrap_api_call(me.serialize)

@bananas.route('/api/user',  methods = ['GET'])
def api_user_get():
    if "user_id" not in session:
        response = {'error': 'No logged in user'}
        return wrap_api_call(response), 403

    return wrap_api_call(User.query.get(int(session["user_id"])).serialize)

@bananas.route('/api/user/cheat', methods=['POST'])
def user_cheat():
    if "bananas" in session:
        session['bananas'] = request.form['bananas']
        User.query.get(session['user_id']).bananas = request.form['bananas']
        gamechange.db.session.commit()

    return api_user_get()

@bananas.route('/api/user/login', methods = ['POST'])
def api_user_login_post():
    if("user_id" in session):
        user = User.query.get(session["user_id"])
        pass
        #already logged in
    else:
        if(not request.json == None):
            username = request.json['username']
            password = request.json['password']
        else :
            try:
                username = request.form['username']
                password = request.form['password']
            except KeyError:
                return wrap_api_call({'error':'Both fields are required'}), 400
        user = User.query.filter_by(username=username).first()

        if user is None:
            return wrap_api_call({'error': 'No such user'}), 403

        if not user.check_password(password):
            return wrap_api_call({'error': 'Incorrect password'}), 403

        #Should check the user isn't banned here!
        session['user_id'] = user.id
    
    response = {'username': user.username, 'bananas': user.bananas}
    return wrap_api_call(response)

@bananas.route('/api/user/logout', methods = ['POST'])
def api_user_logout_post():
    if "user_id" in session:
        session.pop("user_id")
        return wrap_api_call()
    else:
        abort(500)

@bananas.route('/api/user/inventory/<item_id>/use', methods=['POST'])
def api_user_inventory_use(item_id):
    if 'user_id' not in session:
        return wrap_api_call({'error': 'not logged in'}), 403

    item = UserShopItem.query.get(item_id)

    if item is None:
        return wrap_api_call({'error': 'this item does not exist anymore!'}), 403

    if item.user_id != session['user_id']:
        return wrap_api_call({'error': 'this item does not belong to the currently logged in user!'}), 403

    db.session.delete(item)
    db.session.commit()

    return api_user_get()

#post doesn't work yet! Returns 403!
@bananas.route('/api/user', methods = ['POST'])
def api_user_post():
    # username = request.form['username']
    # response = {'username':username}
    response = "lol"
    return wrap_api_call(response)

@bananas.route('/api/inventory', methods=['GET'])
def api_inventory_get():
    if "user_id" in session:
        resp = ""
        return wrap_api_call(resp)
    else:
        abort(403)

@bananas.route('/api/user/register', methods=['POST'])
def api_user_register_post():
    if(not request.json == None):
        username = request.json['username']
        password = request.json['password']
        first_name = request.json['first_name']
        last_name = request.json['last_name']
        email = request.json['email']
    else :
        username = request.form['username']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']

    new_user = User(username, first_name, last_name, email)
    new_user.set_password(password)
    gamechange.db.session.add(new_user)
    gamechange.db.session.commit()
    return wrap_api_call(new_user.serialize)

def wrap_api_call(json=None):
    wrapper = {'_csrf_token': gamechange.generate_csrf_token(), 
        'api_version': 0.1, 
        'hostname': app.config['SERVER_NAME'], 
        'system_time_millis': int(round(time.time() * 1000))
        }
    if(app.config['DEBUG']):
    	wrapper['debug'] = True
    if(app.config['TESTING']):
    	wrapper['testing'] = True
    if(json != None):
        wrapper['data'] = json

    return jsonify(wrapper)
