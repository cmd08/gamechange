from flask.ext.sqlalchemy import SQLAlchemy
from flask import jsonify

db = SQLAlchemy()

class ShopItem(db.Model):
    __tablename__ = "shop_item"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text)
    type = db.Column(db.String(50))
    cost = db.Column(db.Integer)

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
            'name'		    : self.name,
            'cost'          : self.cost,
            'description'   : self.description
        }

class Shelter(ShopItem):
    level = db.Column(db.Integer)
    image_url = db.Column(db.String(512))
    capacity = db.Column(db.Integer)
    food_decay_rate_multiplier = db.Column(db.Integer)
    storage_space = db.Column(db.Integer)

    def __init__(self, name, description, level, image_url, storage_space, food_decay_rate_multiplier):
        self.name = name
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
            'name'                      : self.name,
            'description'               : self.description,
            'level'                     : self.level,
            'image_url'                 : self.image_url,
            'storage_space'             : self.storage_space,
            'food_decay_rate_multiplier': self.food_decay_rate_multiplier
        }

inventory_items = db.Table('inventory_items',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('item_id', db.Integer, db.ForeignKey('shop_item.id'))
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(256), nullable=True)
    first_name = db.Column(db.String(120))
    last_name = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True)
    verified = db.Column(db.Boolean, default=False)
    subscribed = db.Column(db.Boolean, default=True)
    shelter_type_id = db.Column(db.Integer, db.ForeignKey('shop_item.id'))
    shelter = db.relationship('Shelter', backref=db.backref('user', lazy='dynamic'))
    inventory_items = db.relationship('ShopItem', secondary=inventory_items,
        backref=db.backref('user', lazy='dynamic'))

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
       return {
           'id'         : self.id,
           'first_name'	: self.first_name,
           'last_name'	: self.last_name,
           'email'      : self.email,
           'shelter'    : self.shelter.serialize(),
       }

    def __init__(self, username, first_name, last_name, email):
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        
    def __repr__(self):
        return '<User %r>' % self.email

    def set_password(password):
        self.password = password

    def check_password(password):
        return self.password == password

    def set_shelter(shelter):
        self.shelter = shelter
        db.session.commit()

    def add_to_inventory(item):
        self.inventory_items.append(item)
        db.session.commit()



