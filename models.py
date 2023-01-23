from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from datetime import datetime

bcrypt = Bcrypt()
db = SQLAlchemy()


class Character_Appearance(db.Model):
    """Mapping characters to comic issues."""

    __tablename__ = "character_appearances"


    character_id = db.Column(db.Integer,
                        db.ForeignKey('characters.id'),
                        primary_key=True
                        )
    comic_id = db.Column(db.Integer,
                        db.ForeignKey('comics.id'),
                        primary_key=True
                        )

class Comic(db.Model):
    """Comics model.
    
    >>> id = db.Column(db.Integer, primary_key=True)
    >>> name = db.Column(db.Text, nullable=False)
    >>> issue_number = db.Column(db.Text, nullable=False)
    >>> cover_date = db.Column(db.DateTime, nullable=True)
    >>> deck = db.Column(db.Text, default='Unavailable')
    >>> price = db.Column(db.Text, default="4.99")
    >>> cover_img = db.Column(db.Text, default="/static/missing_cover_art.png")
    """

    __tablename__ = 'comics'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    issue_number = db.Column(db.Text, default='N/A')
    cover_date = db.Column(db.Date, nullable=True)
    deck = db.Column(db.Text, default='Unavailable')
    price = db.Column(db.Text, nullable=False, default="4.99")
    cover_img = db.Column(db.Text, default="/static/missing_cover_art.png")

    appear_assignments = db.relationship('Character_Appearance', backref='comics', cascade="all, delete-orphan")
    reading_assignments = db.relationship('Reading_List', backref='comics', cascade="all, delete-orphan")
    order_assignments = db.relationship('Order_Item', backref='comics', cascade="all, delete-orphan")
    

class Character(db.Model):
    """Characters model."""

    __tablename__ = 'characters'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=True)
    real_name = db.Column(db.Text, default='Unavailable')
    deck = db.Column(db.Text, default='Unavailable')
    first_appear_issue_id = db.Column(db.Text, default='Unavailable')
    first_appear_issue_num = db.Column(db.Text, default='Unavailable')
    first_appear_issue_name = db.Column(db.Text, default='Unavailable')
    total_appearances = db.Column(db.Text, default='Unavailable')
    icon_image_url = db.Column(db.Text, default="/static/images/logo/fox-icon-thumb-sm.png")
    original_url = db.Column(db.Text, default="/static/missing_cover_art.png")
    publisher_id = db.Column(db.Text, default='Unavailable')
    publisher_name = db.Column(db.Text, default='Unavailable')

    appear_assignments = db.relationship('Character_Appearance', backref='characters')
    appearances = db.relationship('Comic', secondary='character_appearances', backref='characters')
    character_list_assignments = db.relationship('Character_List', backref='characters', cascade="all, delete-orphan")


class Order(db.Model):
    """Orders model."""

    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    session_id = db.Column(db.Text, unique=True, nullable=False)
    order_status = db.Column(db.Text, nullable=True, default="processing")
    sub_total = db.Column(db.Text, nullable=True)
    tax = db.Column(db.Text, nullable=True)
    shipping = db.Column(db.Text, nullable=True)
    total = db.Column(db.Text, nullable=True)
    customer_name = db.Column(db.Text, nullable=True)
    phone = db.Column(db.Text, nullable=True)
    email = db.Column(db.Text, nullable=True)
    address_line_1 = db.Column(db.Text, nullable=True)
    address_line_2 = db.Column(db.Text, nullable=True)
    city = db.Column(db.Text, nullable=True)
    state = db.Column(db.Text, nullable=True)
    country = db.Column(db.Text, nullable=True)
    created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    items = db.relationship("Comic", 
                            secondary="order_items", 
                            backref="orders"
                            )
                    
    item_assignments = db.relationship("Order_Item", backref="orders", cascade="all, delete-orphan")
    transaction_assignments = db.relationship("User_Orders", backref="orders", cascade="all, delete-orphan")


# *************************************Through Tables************************************

class Character_List(db.Model):
    """Mapping characters to users."""

    __tablename__ = "character_lists"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer, 
                        db.ForeignKey('users.id', ondelete="cascade"), 
                        primary_key=True
                        )

    character_id = db.Column(db.Integer, 
                             db.ForeignKey('characters.id', ondelete="cascade"),
                             primary_key=True
                             )

class Reading_List(db.Model):
    """Mapping comic issues to users."""

    __tablename__ = "reading_lists"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id', ondelete="cascade")
                        )
    comic_id = db.Column(db.Integer,
                        db.ForeignKey('comics.id', ondelete="cascade")
                        )


class Order_Item(db.Model):
    """Mapping comic issues to orders."""

    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    comic_id = db.Column(db.Integer,
                        db.ForeignKey('comics.id', ondelete="cascade"),
                        primary_key=True
                        )
    order_id = db.Column(db.Integer,
                        db.ForeignKey('orders.id', ondelete="cascade"),
                        primary_key=True
                        )


class User_Orders(db.Model):
    """Transaction model."""

    __tablename__ = "user_orders"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)

    user_id = db.Column(db.Integer, 
                        db.ForeignKey('users.id', ondelete="cascade"), 
                        primary_key=True
                        )
    order_id = db.Column(db.Integer, 
                        db.ForeignKey('orders.id', ondelete="cascade"), 
                        primary_key=True
                        )

# *****************************************User Model**********************************************

class User(db.Model):
    """Users model."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    mobile = db.Column(db.Text, nullable=True)
    email = db.Column(db.Text, unique=True, nullable=False)
    username = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)

    characters = db.relationship("Character", 
                                secondary="character_lists", 
                                backref="users"
                                )
    reading = db.relationship("Comic", 
                            secondary="reading_lists", 
                            backref="users"
                            )

    orders = db.relationship("Order",
                            secondary="user_orders",
                            backref="users"
                            )
    assigned_transactions = db.relationship("User_Orders", backref="users", cascade="all, delete-orphan")

    assigned_reading = db.relationship("Reading_List", backref="users", cascade="all, delete-orphan")

    assigned_characters = db.relationship("Character_List", backref="users", cascade="all, delete-orphan")
    

    # format for easy identification in terminal
    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.first_name}, {self.last_name}, {self.email}>"

    @classmethod
    def signup(cls, first_name, last_name, username, email, password):
        """Sign up user.
        
        Hashes password and adds user to database.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode("UTF-8")

        user = User(first_name=first_name,
                    last_name=last_name,
                    username=username,
                    email=email,
                    password=hashed_pwd
                    )
        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with username and password.
        
        Returns the user object whose password hash matches this password.
        
        Returns False if matching user is not found or if password is incorrect
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user
        
        return False
        

# ********************************************Connect Database******************************************
def connect_db(app):
    """Connect this databse to Flask app"""

    db.app = app
    db.init_app(app)