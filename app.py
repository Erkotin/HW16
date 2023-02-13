from datetime import datetime
import json

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

import data
from data import users, offers, orders

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    email = db.Column(db.String(100))
    role = db.Column(db.String(20))
    phone = db.Column(db.String(100))

    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    address = db.Column(db.String)
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


class Offer(db.Model):
    __tablename__ = 'offer'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}

with app.app_context():
    db.create_all()

    for user_data in data.users:
        db.session.add(User(**user_data))
        db.session.commit()

    for order_data in data.orders:
        order_data['start_date'] = datetime.strptime(order_data['start_date'], '%m/%d/%Y').date()
        order_data['end_date'] = datetime.strptime(order_data['end_date'], '%m/%d/%Y').date()
        db.session.add(Order(**order_data))
        db.session.commit()

    for offer_data in data.offers:
        db.session.add(Offer(**offer_data))
        db.session.commit()


@app.route('/users', methods=['GET', 'POST'])
def users():
    if request.method == 'GET':
        users = User.query.all()
        result = [usr.to_dict() for usr in users]
        return json.dumps(result), 200, {'Content-Type': 'application/json; charset=utf-8'}
    elif request.method == 'POST':
        user_data = json.loads(request.data)
        db.session.add(User(**user_data))
        db.session.commit()
        return '', 201

@app.route('/users/<int:uid>', methods=['GET', 'PUT', 'DELETE'])
def user(uid: int):
    if request.method == 'GET':
        user = User.query.get(uid).to_dict()
        return json.dumps(user), 200, {'Content-Type': 'application/json; charset=utf-8'}
    elif request.method == 'DELETE':
        user = User.query.get(uid)
        db.session.delete(user)
        db.session.commit()
        return '', 204
    elif request.method == 'PUT':
        user_data = json.loads(request.data)
        user = User.query.get(uid)
        user.first_name = user_data['first_name']
        user.role = user_data['role']
        user.phone = user_data['phone']
        user.email = user_data['email']
        user.age = user_data['age']
        return '', 204

@app.route('/orders', methods=['GET', 'POST'])
def orders():
    if request.method == 'GET':
        orders = Order.query.all()
        result = []
        for order in orders:
            ord_dict = order.to_dict()
            ord_dict['start_date'] = str(ord_dict['start_date'])
            ord_dict['end_date'] = str(ord_dict['end_date'])
            result.append(ord_dict)
        return json.dumps(result), 200, {'Content-Type': 'application/json; charset=utf-8'}
    elif request.method == 'POST':
        order_data = json.loads(request.data)
        db.session.add(Order(**order_data))
        db.session.commit()
        return '', 201

@app.route('/orders/<int:oid>', methods=['GET', 'PUT', 'DELETE'])
def order(oid: int):
    if request.method == 'GET':
        order = Order.query.get(oid)
        ord_dict = order.to_dict()
        ord_dict['start_date'] = str(ord_dict['start_date'])
        ord_dict['end_date'] = str(ord_dict['end_date'])
        return json.dumps(ord_dict), 200, {'Content-Type': 'application/json; charset=utf-8'}
    elif request.method == 'DELETE':
        order = Order.query.get(oid)
        db.session.delete(order)
        db.session.commit()
        return '', 204
    elif request.method == 'PUT':
        order_data = json.loads(request.data)
        order = Order.query.get(oid)
        order_data['start_date'] = datetime.strptime(order_data['start_date'], '%Y-%m-%d').date()
        order_data['end_date'] = datetime.strptime(order_data['end_date'], '%Y-%m-%d').date()
        order.name = order_data['name']
        order.description = order_data['description']
        order.start_date = (order_data['start_date'])
        order.end_date = (order_data['end_date'])
        order.price = order_data['price']
        order.customer_id = order_data['customer_id']
        order.executor_id = order_data['executor_id']
        db.session.add(order)
        db.session.commit()
        return '', 204

@app.route('/offers', methods=['GET', 'POST'])
def offers():
    if request.method == 'GET':
        offers = Offer.query.all()
        result = [offer.to_dict() for offer in offers]
        return json.dumps(result), 200, {'Content-Type': 'application/json; charset=utf-8'}
    elif request.method == 'POST':
        offer_data = json.loads(request.data)
        db.session.add(Offer(**offer_data))
        db.session.commit()
        return '', 201

@app.route('/offers/<int:oid>', methods=['GET', 'PUT', 'DELETE'])
def offer(oid: int):
    if request.method == 'GET':
        offer = Offer.query.get(oid).to_dict()
        return json.dumps(offer), 200, {'Content-Type': 'application/json; charset=utf-8'}
    elif request.method == 'DELETE':
        offer = Offer.query.get(oid)
        db.session.delete(offer)
        db.session.commit()
        return '', 204
    elif request.method == 'PUT':
        offer_data = json.loads(request.data)
        offer = Offer.query.get(oid)
        offer.order_id = offer_data['order_id']
        offer.executor_id = offer_data['executor_id']
        db.session.add(offer)
        db.session.commit()
        return '', 204

if __name__ == '__main__':
    app.run()
