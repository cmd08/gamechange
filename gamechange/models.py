from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm.collections import attribute_mapped_collection
from flask import jsonify
from datetime import datetime

db = SQLAlchemy()

class ShopItem(db.Model):
    __tablename__ = "shop_item"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text)
    type = db.Column(db.String(50))
    cost = db.Column(db.Integer)
    image_url = db.Column(db.String(512))

    __mapper_args__ = {
        'polymorphic_identity' : 'shop_item',
        'polymorphic_on' : type
    }

    def __init__(self, name, cost, description):
        self.name = name
        self.cost = cost
        self.description = description

    def __repr__(self):
        return self.name
        
    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id'            : self.id,
            'name'          : self.name,
            'cost'          : self.cost,
            'description'   : self.description,
            'type'          : self.type,
        }

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(120))
    last_name = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True)
    verified = db.Column(db.Boolean, default=False)
    subscribed = db.Column(db.Boolean, default=True)
    last_checked = db.Column(db.DateTime, default=datetime(1970, 1, 1, 0, 0, 0, 0))
    # username = db.Column() text
    healthgraph_api_key = db.Column(db.String(32), unique=True)
    healthgraph_activities = db.relationship('HealthgraphActivity', backref='User', lazy='dynamic')
    bananas = db.Column(db.Integer, default=0)
    inventory_items = db.relationship("UserShopItem")


    def isValid(self):
        self.error = dict()
        valid = True
        if not User.query.filter_by(email=self.email).first() == None :
            self.error['email'] = "Oops! Looks like you've already signed up!"
            valid = False
        if '@' not in self.email:
            self.error['email'] = "Please check your e-mail address is valid."
            valid = False
        if self.first_name == '':
            valid = False
            self.error['first_name'] = "Please enter your first name."
        if self.last_name == '':
            valid = False
            self.error['last_name'] = "Please enter your last name."
        if self.email == '':
            valid = False
            self.error['email'] = "Please provide an e-mail address."
        return valid

    @property
    def serialize(self):
      """Return object data in easily serializeable format"""
      resp = {
        'id'                    : self.id,
        'username'              : self.username,
        'first_name'            : self.first_name,
        'last_name'             : self.last_name,
        'email'                 : self.email,
        'bananas'               : self.bananas,
        'username'              : self.username,
        'last_checked'          : self.last_checked.isoformat(),
        #'health'        : self.health,
        'inventory'             : [i.serialize for i in self.inventory_items],
      }
      if (self.healthgraph_api_key is not None):
            resp['healthgraph_api_key'] = self.healthgraph_api_key
      return resp

    def __init__(self, username, first_name, last_name, email):
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        
    def __repr__(self):
        return '<User %r>' % self.email

    def set_password(self, password):
        self.password = password

    def check_password(self, password):
        return self.password == password

    def set_shelter(self, shelter):
        self.shelter = shelter
        db.session.commit()

    def add_to_inventory(self, item):
        if (self.bananas - item.cost < 0):
            raise ValueError('You do not have sufficient bananas!')

        self.bananas = self.bananas - item.cost
        self.inventory_items.append(UserShopItem(item))


class HealthgraphActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    activity_type = db.Column(db.String(32))
    calories = db.Column(db.Integer)
    user = db.Column(db.Integer, db.ForeignKey('user.id'))
    bananas_earned = db.Column(db.Integer)
    banked = db.Column(db.Boolean, default=False)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'id'             : self.id,
           'activity_type'  : self.activity_type,
           'calories'       : self.calories,
           'user'           : self.user,
           'bananas_earned' : self.bananas_earned,
           'banked'         : self.banked
       }

    def __init__(self, id, activity_type, calories, user, bananas_earned):
        self.id = id
        self.activity_type = activity_type
        self.calories = calories
        self.user = user
        self.bananas_earned = bananas_earned

    # def __repr__(self):
    #     return '<HealthgraphActivity %r>' % self.activity_type

    def bank_bananas(self):
        User.query.get(self.user).bananas = User.query.get(self.user).bananas + self.bananas_earned
        self.banked = True


class UserShopItem(db.Model):
    __tablename__ = 'user_shop_item'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    shop_item_id = db.Column(db.Integer, db.ForeignKey('shop_item.id'), nullable=False)
    shop_item = db.relationship("ShopItem")
    purchase_date = db.Column(db.DateTime, nullable=False)

    def __init__(self, item):
        self.purchase_date = datetime.now()
        self.shop_item_id = item.id

    @property
    def serialize(self):
        return {
            'inventory_id': int(self.id),
            'purchase_date' : self.purchase_date.isoformat(),
            'item'     : self.shop_item.serialize,
        }


class Shelter(ShopItem):
    level = db.Column(db.Integer)
    capacity = db.Column(db.Integer)
    food_decay_rate_multiplier = db.Column(db.Integer)
    storage_space = db.Column(db.Integer)

    def __init__(self, name, cost, description, level, image_url, storage_space, food_decay_rate_multiplier):
        self.name = name
        self.cost = cost
        self.description = description
        self.level = level
        self.image_url = image_url
        self.storage_space = storage_space
        self.food_decay_rate_multiplier = food_decay_rate_multiplier
    
    __mapper_args__ = {
        'polymorphic_identity' : 'shelter'
    }

    @property
    def serialize(self):
        return {
            'id'                        : self.id,
            'cost'                      : self.cost,
            'name'                      : self.name,
            'description'               : self.description,
            'level'                     : self.level,
            'image_url'                 : self.image_url,
            'storage_space'             : self.storage_space,
            'food_decay_rate_multiplier': self.food_decay_rate_multiplier,
            'type'                      : self.type,
        }


class Supplies(ShopItem):
    health_points = db.Column(db.Integer)
    shelf_life = db.Column(db.Integer, default=None)
    size = db.Column(db.Integer, default=1)
    

    def __init__(self, name, cost, description, image_url, health_points, shelf_life, size):
        self.name = name
        self.cost = cost
        self.description = description
        self.image_url = image_url
        self.health_points = health_points
        self.shelf_life = shelf_life
        self.size = size
    
    __mapper_args__ = {
        'polymorphic_identity' : 'supply'
    }

    @property
    def serialize(self):
        return {
            'id'                        : self.id,
            'name'                      : self.name,
            'cost'                      : self.cost,
            'description'               : self.description,
            'image_url'                 : self.image_url,
            'health_points'             : self.health_points,
            'shelf_life'                : self.shelf_life,
            'size'                      : self.size,
            'type'                      : self.type,
        }
