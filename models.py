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
    cover_date = db.Column(db.Date, default='Unavailable')
    deck = db.Column(db.Text, default='Unavailable')
    price = db.Column(db.Text, default="4.99")
    cover_img = db.Column(db.Text, default="/static/missing_cover_art.png")

    assignments = db.relationship('Character_Appearance', backref='comics', cascade="all, delete-orphan")

class Character(db.Model):
    """Characters model."""

    __tablename__ = 'characters'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=True)
    real_name = db.Column(db.Text, nullable=True)
    deck = db.Column(db.Text, nullable=True)
    first_appear_issue_id = db.Column(db.Integer, nullable=True)
    first_appear_issue_num = db.Column(db.Integer, nullable=True)
    first_appear_issue_name = db.Column(db.Text, nullable=True)
    total_appearances = db.Column(db.Integer, nullable=True)
    icon_image_url = db.Column(db.Text, default="/static/images/logo/fox-icon-thumb-sm.png")
    original_url = db.Column(db.Text, default="/static/missing_cover_art.png")
    publisher_id = db.Column(db.Integer, nullable=True)
    publisher_name = db.Column(db.Text, nullable=True)

    assignments = db.relationship('Character_Appearance', backref='characters')
    appearances = db.relationship('Comic', secondary='character_appearances', backref='characters')



class Review(db.Model):
    """Reviews model."""

    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    title = db.Column(db.Text, nullable=False)
    stars = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)

    assignments = db.relationship("Comic_Review", backref='reviews', cascade='all, delete-orphan')


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
    created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    items = db.relationship("Order_Item", backref="orders", cascade='all, delete-orphan')

class Transaction(db.Model):
    """Orders model."""

    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    order_id = db.Column(db.Integer, unique=True, nullable=False)
    code = db.Column(db.Text, unique=True, nullable=False)
    type = db.Column(db.Text, nullable=False)
    payment_status = db.Column(db.Text, nullable=False, default="processing")
    created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
    notes = db.Column(db.Text, nullable=True)

# *************************************Through Tables************************************

class Character_List(db.Model):
    """Mapping characters to users."""

    __tablename__ = "character_lists"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer, 
                        db.ForeignKey('users.id', 
                        ondelete="cascade"), 
                        primary_key=True
                        )

    character_id = db.Column(db.Integer, 
                             db.ForeignKey('characters.id', 
                             ondelete="cascade"),
                             primary_key=True
                             )

class Reading_List(db.Model):
    """Mapping comic issues to users."""

    __tablename__ = "reading_lists"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id',
                        ondelete="cascade"),
                        primary_key=True
                        )
    comic_id = db.Column(db.Integer,
                        db.ForeignKey('comics.id',
                        ondelete="cascade"),
                        primary_key=True
                        )
    read = db.Column(db.Boolean, default=False)

class Comic_Review(db.Model):
    """Mapping reviews to comic issues."""

    __tablename__ = "comic_reviews"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id',
                        ondelete="cascade"),
                        primary_key=True
                        )
    review_id = db.Column(db.Integer,
                        db.ForeignKey('reviews.id',
                        ondelete="cascade"),
                        primary_key=True
                        )
    comic_id = db.Column(db.Integer,
                        db.ForeignKey('comics.id',
                        ondelete="cascade"),
                        primary_key=True
                        )

class Order_Item(db.Model):
    """Mapping comic issues to orders."""

    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    comic_id = db.Column(db.Integer,
                        db.ForeignKey('comics.id',
                        ondelete="cascade"),
                        primary_key=True
                        )
    order_id = db.Column(db.Integer,
                        db.ForeignKey('orders.id',
                        ondelete="cascade"),
                        primary_key=True
                        )
    quantity = db.Column(db.Integer, nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
    updated = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
    notes = db.Column(db.Text, nullable=True)



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

    characters = db.relationship("User", 
                                secondary="character_lists", 
                                primaryjoin=(Character_List.user_id == id), 
                                secondaryjoin=(Character_List.character_id == id)
                                )
    reading = db.relationship("User", 
                             secondary="reading_lists", 
                             primaryjoin=(Reading_List.user_id == id),
                             secondaryjoin=(Reading_List.comic_id == id)
                             )
    reviews = db.relationship("User", 
                              secondary="comic_reviews", 
                              primaryjoin=(Comic_Review.user_id == id),
                              secondaryjoin=(Comic_Review.review_id == id)
                              )

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