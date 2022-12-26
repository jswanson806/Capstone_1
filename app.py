
import os
import requests, json, pdb
from flask import Flask, jsonify, make_response, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User, Character, Comic, Review, Order, Transaction
from forms import UserSignUpForm, EditUserForm, LoginForm, UserSignInForm
from secret import COMIC_API_KEY

CURR_USER_KEY = "curr_user"



app = Flask(__name__)

# API URLs
COMIC_BASE = 'https://comicvine.gamespot.com/api'
COMIC_CHARACTERS = 'https://comicvine.gamespot.com/api/characters'
COMIC_CHARACTER = 'https://comicvine.gamespot.com/api/character/4005-'
COMIC_ISSUE = 'https://comicvine.gamespot.com/api/issue/4000-'

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



#*****************************Methods******************************
def get_comic_issue(issue_id):

    # check for comic issue in SQL db
    exists = db.session.query(db.exists().where(Comic.id == issue_id)).scalar()
    
    if exists:
        # query SQL db comic
        comic = Comic.query.get(issue_id)  
        return comic
    
    else:
        key = COMIC_API_KEY
        url = COMIC_ISSUE + f'{issue_id}'

        params = {"api_key":key, 
                  "field_list":"id,name,deck,cover_date,issue_number,image,first_appearance_characters",
                  "format":"json"
                 }

        headers = {
                  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
                  "Content-Type": "application/json"
                  }

        res = requests.get(url, headers=headers, params=params)

        data = res.json()

        new_comic = Comic(id = data['results']['id'],
                        name = data['results']['name'],
                        issue_number = data['results']['issue_number'],
                        cover_date = data['results']['cover_date'],
                        cover_img = data['results']['image']['original_url'],
                        deck = data['results']['deck'],
                        )
    
        db.session.add(new_comic)
        db.session.commit()

        return new_comic
        

def get_character_appearances(character_id):
    key = COMIC_API_KEY
    url = COMIC_CHARACTER + f'{character_id}'
    search_results = []

    params = {"api_key":key, 
              "field_list":"issue_credits",
              "format":"json"
            }

    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    "Content-Type": "application/json"
    }

    res = requests.get(url, headers=headers, params=params)

    data = res.json()
    
    issue_credits = data['results']['issue_credits']

    # filter out issue titles that are not real titles
    forbidden_names = ['TPB','HC','HC/TPB', 'TPB/HC', 'HC\TPB', 'TPB\HC', 'Chapter','Volume', '', 'SC']

    # additional filters for issue titles that are not full title names during loop
    for i in issue_credits:
        if i['name'] not in forbidden_names and i['name'] != None and not i['name'].startswith(('Volume', 'Chapter', 'Book', 'Part', 'Vol.')):
            id = i['id']
            name = i['name']
            issue = {'id': id, 'name': name}
            search_results.append(issue)
    
    return search_results

def search_characters(search_term):
    """
    Returns characters with similar names to the search_term.

    Limits calls to the API:
    If characters do not exist in the SQL db already ->
    call the API and generate new character instances from the returned data ->
    Add the characters to the SQL db and return the list of character SQLAlchemy objects
    """

    # check for characters similar to search_term in SQL db
    exists = db.session.query(db.exists().where(Character.name.like(f'%{search_term}%'))).scalar()

    # if characters are already present in SQL db, query the characters and return them
    if exists:
        characters = db.session.query(Character).filter(Character.name.like(f'%{search_term}%')).from_self()
        return characters

    # if no matching characters are found in SQL db, query the API
    # -> iterate over response data and add characters to the database
    # -> return the list of characters from the API

    else:

        key = COMIC_API_KEY
        url = COMIC_CHARACTERS      
        search_results = []

        params = {"api_key":key, 
                       "field_list":"id,name,real_name,aliases,deck,first_appeared_in_issue,count_of_issue_appearances,image,api_detail_url,publisher",
                       "filter":f"name:{search_term}",
                       "format":"json"
                       }

        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        "Content-Type": "application/json"
        }

        res = requests.get(url, headers=headers, params=params)

        data = res.json()

        # count of returned characters from api search
        results_count = data['number_of_page_results']

        # iterate over data and extract character information
        for i in range (0,results_count):
            id = data['results'][i]['id']
            name = data['results'][i]['name']
            real_name = data['results'][i]['real_name']
            deck = data['results'][i]['deck']
            first_appear_issue_id = data['results'][i]['first_appeared_in_issue']['id']
            first_appear_issue_num = data['results'][i]['first_appeared_in_issue']['issue_number']
            first_appear_issue_name = data['results'][i]['first_appeared_in_issue']['name']
            total_appearances = data['results'][i]['count_of_issue_appearances']
            icon_image_url = data['results'][i]['image']['icon_url']
            original_url = data['results'][i]['image']['original_url']
            publisher_id = data['results'][i]['publisher']['id']
            publisher_name = data['results'][i]['publisher']['name']

            # create new character instances
            new_character = Character(id=id,
                                name=name, 
                                real_name=real_name, 
                                deck=deck, 
                                first_appear_issue_id=first_appear_issue_id,
                                first_appear_issue_name=first_appear_issue_name,
                                first_appear_issue_num=first_appear_issue_num,                 
                                total_appearances=total_appearances, 
                                icon_image_url=icon_image_url,
                                original_url=original_url,
                                publisher_id=publisher_id,
                                publisher_name=publisher_name
                                )
            # add and commit new character instance to the SQL db                    
            db.session.add(new_character)
            db.session.commit()
            # append character SQLAlchemy object to the search_results list
            search_results.append(new_character)

        return search_results


#***************Homepage | Sign-in | Sign-up | Logout****************

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

#***************************************Character Routes**********************************

@app.route('/characters')
def find_characters():
    """Find characters matching keyword search."""
    # get matching results from api - limit 100
    search_res = search_characters('Kraven')

    
    return render_template('characters-search.html', characters=search_res)

@app.route('/<int:character_id>')
def show_character_details(character_id):
    """Show single character details page."""
    character = Character.query.get_or_404(character_id)

    appearances = get_character_appearances(character_id)
    

    return render_template('character-details.html', character=character, appearances=appearances)

#***************************************Cart Routes***************************************

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
def show_comic_details(comic_id):
    """Remove item from cart in session."""
    comic = get_comic_issue(comic_id)
    return render_template('comic-details.html', comic=comic)

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

    return redirect(f'/comic/{review_id}')

