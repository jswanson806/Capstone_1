from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

bcrypt = Bcrypt()
db = SQLAlchemy()

class Users(db.Model):
    """Users model."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    mobile = db.Column(db.Text(10), nullable=True)
    email = db.Column(db.Email, unique=True, nullable=False)
    username = db.Column(db.Text(20), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)

class Character(db.Model):
    """Characters model."""

    __tablename__ = 'characters'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    alter_ego = db.Column(db.Text, nullable=True)
    powers = db.Column(db.Text, nullable=True)
    appears_in = db.Column(db.Text, nullable=False)

class Comic(db.Model):
    """Comics model."""

    __tablename__ = 'comics'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.Text, nullable=False)
    issue_number = db.Column(db.Text, nullable=False)
    publisher = db.Column(db.Text, nullable=False)
    published_date = db.Column(db.DateTime, nullable=False)
    author = db.Column(db.Text, nullable=False)
    illustrator = db.Column(db.Text, nullable=False)
    price = db.Column(db.Text, nullable=False)
    cover_img = db.Column(db.Text, default="/static/missing_cover_art.png")


class Review(db.Model):
    """Reviews model."""

    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    title = db.Column(db.Text, nullable=False)
    stars = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text(500), nullable=False)


class Order(db.Model):
    """Orders model."""

    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    session_id = db.Column(db.Integer, unique=True, nullable=False)
    token = db.Column(db.Text, unique=True, nullable=False)
    order_status = db.Column(db.Text, nullable=False, default="processing")
    sub_total = db.Column(db.Text, nullable=False)
    tax = db.Column(db.Text, nullable=False)
    shipping = db.Column(db.Text, nullable=False)
    total = db.Column(db.Text, nullable=False)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    mobile = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)
    address_line_1 = db.Column(db.Text, nullable=False)
    address_line_2 = db.Column(db.Text, nullable=True)
    city = db.Column(db.Text, nullable=False)
    state = db.Column(db.Text, nullable=False)
    country = db.Column(db.Text, nullable=False)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=True)
    notes = db.Column(db.Text, nullable=True)

class Transaction(db.Model):
    """Orders model."""

    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    order_id = db.Column(db.Integer, unique=True, nullable=False)
    code = db.Column(db.Text, unique=True, nullable=False)
    type = db.Column(db.Text, nullable=False)
    payment_status = db.Column(db.Text, nullable=False, default="processing")
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=True)
    notes = db.Column(db.Text, nullable=True)