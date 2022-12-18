
import os
import requests

from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User, Character, Comic, Review, Order, Transaction
from forms import UserSignUpForm, EditUserForm, LoginForm, UserSignInForm
from secret import API_SECRET_KEY
import pdb

CURR_USER_KEY = "curr_user"

COMIC_API_BASE_URL = 'https://comicvine.gamespot.com/api'

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///comicbook_store'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)

#***********************Homepage | Sign-in | Sign-up**********************

@app.before_request
def add_user_to_g():
    """If we are logged in, add current user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

def login(user):
    """Login user."""

    session[CURR_USER_KEY] = user.id

def logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/')
def homepage():
    return render_template('shop.html')


@app.route('/signup', methods=["GET", "POST"])
def sign_up_page():
    """Show the user sign-up page.
    
    Show form if GET. 
    If valid, create new user -> add user to database -> redirect to homepage.
    """
    form = UserSignUpForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data
            )
            db.session.commit()
        # if user creation fails, flash message and serve the form again
        except IntegrityError:
            flash("Username is taken", 'danger')
            return render_template('sign-up.html', form=form)

        login(user)

        return redirect('/')
    # if validations fails, serve the form again
    else:
        return render_template('sign-up.html', form=form)


@app.route('/signin', methods=["GET", "POST"])
def sign_in_page():
    """Show the user sign-in page.
    
    Show form if GET. 
    If valid, log-in user -> update user in session -> redirect to homepage.
    """
    form = UserSignInForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)
        # if user authentication success -> login user -> flash welcome msg
        if user:
            login(user)
            flash(f"Welcome back, {user.username}!", "success")
            return redirect('/')

        # if user auth fails -> flash invalid msg
        flash("Invalid information.", "danger")

    # if form validation fails, rerender the form
    return render_template('sign-in.html', form=form)


#*************************User Routes*************************

@app.route('/users/<int:user_id>/account')
def show_user_profile(user_id):
    """Show the user account information."""
    if g in session:

        user = User.query.get_or_404(user_id)
        return render_template('my-account.html', user=user)
        
    flash('Login to view this page.', "danger")
    return redirect('/signin')


@app.route('/users/<int:user_id>/edit', methods=["GET", "POST"])
def edit_user_profile(user_id):
    """Apply changes to the user information.
    
    Show form if GET. 
    If valid, update user information in db -> redirect to user account page.
    """

    return redirect(f'/users/{user_id}/account')


@app.route('/users/<int:user_id>/wishlist')
def show_user_wishlist(user_id):
    """Show all user wishlisted items."""

    return render_template('wishlist.html')


@app.route('/users/<int:user_id>/add_wishlist', methods=["POST"])
def add_wishlist_item(user_id):
    """Add item to user wishlist."""

    return redirect('/')


@app.route('/users/<int:user_id>/remove_wishlist', methods=["POST"])
def remove_wishlist_item(user_id):
    """Remove item from user wishlist."""

    return redirect('/')


@app.route('/users/<int:user_id>/characters')
def show_saved_characters(user_id):
    """Show list of user's saved characters."""

    return render_template('characters-list.html')


@app.route('/users/<int:user_id>/add_character', methods=["POST"])
def add_character(user_id):
    """Add character to list of user's saved characters."""

    return redirect(f'/users/{user_id}/characters')
    

@app.route('/users/<int:user_id>/remove_character', methods=["POST"])
def remove_character(user_id):
    """Remove character from list of user's saved characters."""

    return redirect(f'/users/{user_id}/characters')

#******************************************Character Routes***************************************

@app.route('/characters/<int:character_id>')
def show_character_details(character_id):
    """Show details for specific character."""

    return render_template('single-product.html')

#******************************************Cart Routes***************************************

@app.route('/cart')
def show_cart_details():
    """Show contents of current cart in session."""

    return render_template('cart.html')


@app.route('/cart/add', methods=["POST"])
def add_to_cart():
    """Add item to cart in session."""

    return redirect('/cart')


@app.route('/cart/remove', methods=["POST"])
def remove_from_cart():
    """Remove item from cart in session."""

    return redirect('/cart')


@app.route('/cart/checkout', methods=["GET", "POST"])
def show_checkout_form():
    """Show checkout form.
    
    Show form if GET.
    If valid, process payment -> create new order -> save order to db
    """

    return render_template('checkout.html')

#******************************************Comic Routes***************************************

@app.route('/comic/<int:comic_id>')
def show_comic_details():
    """Remove item from cart in session."""

    return redirect('/')

#******************************************Review Routes***************************************

@app.route('/comic/review/add', methods=["GET", "POST"])
def add_review(comic_id):
    """Add review to comic issue.
    
    Show form if GET. If valid, update review -> redirect to comic details page.
    """

    return redirect(f'/comic/{comic_id}')


@app.route('/comic/review/<int:review_id>/remove', methods=["POST"])
def remove_review(review_id):
    """Remove review from comic issue."""

    return redirect(f'/comic/{comic_id}')
