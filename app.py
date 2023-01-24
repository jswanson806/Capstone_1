
import os
import collections.abc
collections.Container = collections.abc.Container
collections.Mapping = collections.abc.Mapping
collections.MutableMapping = collections.abc.MutableMapping
collections.Iterable = collections.abc.Iterable
collections.MutableSet = collections.abc.MutableSet
collections.Callable = collections.abc.Callable

from flask import Flask, render_template, request, flash, redirect, session, g, abort
from flask_mail import Mail, Message
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User, Character, Comic, Order
from forms import UserSignUpForm, EditUserForm, UserSignInForm
from methods import search_characters, find_single_character, find_character_appearances, add_character_to_db, add_comic_to_db, get_comic_issue, clear_session_cart
import stripe


CURR_USER_KEY = "curr_user"
stripe.api_key = os.environ.get('STRIPE_TEST_API_KEY', 'sk_test_51MNeg0DugXxFxym6nqUpiTKKtRpdLwRjM4Hix8NKPObBVtDYIVuW8FxTbLipSvxvt4Oj45yjeUe2iFUTTLVrdadF00KclEHSAC')

app = Flask(__name__)

endpoint_secret = 'whsec_MK26BTdNTz9h18jc582zBr8zVSvXgMos'

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///comicbook_store'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['COMIC_API_KEY'] = os.environ.get('COMIC_API_KEY', '6097d6aeb080923e8927570f0ff9ac6f3292fe0a')
toolbar = DebugToolbarExtension(app)

connect_db(app)

mail = Mail(app)

#************************Error Handlers*****************************

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

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
    """Show shop main page."""

    if g.user:
        user = g.user
    else:
        user = None
        
    return render_template('about-us.html', user=user)


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
            flash("Username or Email is taken", 'danger')
            return render_template('sign-up.html', form=form)

        # send welcome email
        msg = Message('Welcome to Fox Comics!', sender = 'foxcomicsllc@gmail.com', recipients = [form.email.data])
        msg.html = render_template("welcome-email.html")
        mail.send(msg)

        # log the new user in
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
        return redirect('/signin')

    # if form validation fails, rerender the form
    return render_template('sign-in.html', form=form)

@app.route('/logout')
def sign_out_user():
    """logs the user out."""
    logout()
    
    return redirect('/signin')


#*************************User Routes*************************

@app.route('/users/<int:user_id>/account', methods=["GET", "POST"])
def show_user_profile(user_id):
    """Show the user account information."""

    if g.user.id != user_id:
        flash("Access Unauthorized.", "danger")
        return redirect('/signin')
    # get the user object from the db
    user = User.query.get_or_404(user_id)
    # initialize the form
    form = EditUserForm(obj=user)
    # check the session for a user key
    if CURR_USER_KEY in session:
        if form.validate_on_submit():
            user.username=form.username.data
            user.first_name=form.first_name.data
            user.last_name=form.last_name.data
            user.mobile=form.mobile.data
            user.email=form.email.data
            user = User.authenticate(form.username.data, form.password.data)
            # check for authentication success
            if user:
                # commit the changes to the user object
                db.session.commit()
                return redirect(f'/users/{user.id}/account')
            else:
                # flash msg if authentication fails
                flash('Incorrect password')
                return redirect('/')
    orders = user.orders

    return render_template('my-account.html', form=form, orders=orders)


@app.route('/users/<int:user_id>/reading')
def show_user_reading_list(user_id):
    """Show user reading list."""

    if g.user.id != user_id:
        flash("Access unauthorized", "danger")
        return redirect('/signin')

    reading_list = g.user.reading

    return render_template('reading-list.html', reading_list=reading_list)


@app.route('/users/reading_list/<int:comic_id>', methods=["POST"])
def add_reading_list_item(comic_id):
    """Add item to user reading list."""
    
    if not g.user:
        flash("Login to save comics", "danger")
        return redirect('/')

    # if comic is in db, query the db and return comic
    # else query api and return comic object

    # check for comic issue in SQL db
    exists = db.session.query(db.exists().where(Comic.id == comic_id)).scalar()
    
    if exists:
        # query SQL db comic
        comic = Comic.query.get(comic_id)
    else:
        # query api for comic, returns comic object instance
        new_comic = get_comic_issue(comic_id)

        # add the comic to the db if it does not already exist, returns db comic object
        comic = add_comic_to_db(new_comic)
    
    # get the comic object from the db
    comic = Comic.query.get_or_404(comic_id)
    # get the user from the db
    user = User.query.get(g.user.id)
    # add the comic object to the users reading list
    user.reading.append(comic)
    db.session.commit()

    return redirect(f'/comic/{comic.id}')


@app.route('/users/<int:comic_id>/remove_comic', methods=["POST"])
def remove_reading_list_item(comic_id):
    """Remove comic from user reading list."""

    if not g.user:
        flash("Access Unauthorized.", "danger")
        return redirect('/signin')
    # get the comic object from the db
    comic = Comic.query.get_or_404(comic_id)
    # remove the comic object from the users reading list
    g.user.reading.remove(comic)

    db.session.commit()

    return redirect(f'/users/{g.user.id}/reading')


@app.route('/users/<int:user_id>/characters')
def show_saved_characters(user_id):
    """Show list of user's saved characters."""

    if g.user.id != user_id:
        flash("Access unauthorized.", "danger")
        return redirect('/signin')
    
    character_list = g.user.characters

    
    return render_template('characters-list.html', character_list=character_list)


@app.route('/users/characters/<int:character_id>', methods=["POST"])
def add_character(character_id):
    """Add character to list of user's saved characters.
    >>> if character is in db, query the db and return character object
    >>> else query api and return character object
    """

    if not g.user:
        flash("Login to save comics", "danger")
        return redirect('/')
        
    # if character is in db, query the db and return character
    # else query api and return character object

    # check for comic issue in SQL db
    exists = db.session.query(db.exists().where(Character.id == character_id)).scalar()
    
    if exists:
        # query SQL db character
        character = Character.query.get(character_id)
    else:
        # query api for character, returns character object instance
        new_character = find_single_character(character_id)

        # add the character to the db, returns db character object
        character = add_character_to_db(new_character)

    # get the user from the db
    user = User.query.get_or_404(g.user.id)
    # append the character to user.characters
    user.characters.append(character)

    db.session.commit()

    return redirect(f'/characters/{character_id}')
        
    

@app.route('/users/<int:character_id>/remove_character', methods=["POST"])
def remove_character(character_id):
    """Remove character from list of user's saved characters."""
    
    if not g.user:
        flash("Access Unauthorized.", "danger")
        return redirect('/signin')
    
    character = Character.query.get_or_404(character_id)
    g.user.characters.remove(character)
    db.session.commit()


    return redirect(f'/users/{g.user.id}/characters')

#***************************************Character Routes**********************************

@app.route('/characters')
def find_characters():
    """Find characters matching keyword search."""
    args = request.args['prod-search']
    # get matching results from api (limit 100) or local db if characters exist already
    search_res = search_characters(args)
    
    return render_template('characters-search.html', characters=search_res)


@app.route('/characters/<int:character_id>')
def show_character_details(character_id):
    """ 
    Show single character details page.
    >>> Extract character appearances (comics) from response data ->
    >>> Filter out titles that are not full titles ->
    >>> Append the character appearances to an appearances list as:
    >>> appearances [
    >>>         {
    >>>         'id': id, 
    >>>         'name': name
    >>>         }
    >>>     ]
    >>> Check for the character in the db ->
    >>> Else, create new instance -> save to db
    >>> 
    >>> Pass character instance and appearances list to route.
    """
    
    # query api for single character and return character instance
    appearances = find_character_appearances(character_id)


    # check for character in SQL db
    exists = db.session.query(db.exists().where(Character.id == character_id)).scalar()

    # if character is already present in SQL db, query the character
    if exists:
        character = Character.query.get(character_id)
        return render_template('character-details.html', character=character, appearances=appearances)
    # character does not exist, create new instance
    else:
        character = find_single_character(character_id)

        return render_template('character-details.html', character=character, appearances=appearances)


#***************************************Cart Routes***************************************

@app.route('/cart', methods=["GET"])
def show_session_cart():
    """Show contents of current cart in session."""
    cart_contents = []
    subtotal = 0

    if 'cart' in session:

        for item in session['cart']:
            # get the comic from the database
            comic = Comic.query.get(item['id'])
            
            # ignore None Type objects
            if comic:
                # calculate the subtotal of the item -> comic.name is key, value is the quantity ->
                # coerce the item quantity and comic price to float ->
                # round the result to 2 decimals
                item_subtotal = round(float(item[comic.name]) * float(comic.price), 2)
                # append the comic to the cart_contents list
                cart_contents.append((comic, int(item[comic.name]), item_subtotal))
                # update the subtotal with the price of all comics in the session cart
                subtotal = round(subtotal + item_subtotal, 2)

    return render_template('cart.html', cart_contents=cart_contents, subtotal=subtotal)


@app.route('/cart/<int:comic_id>/add', methods=["POST"])
def add_item_to_session_cart(comic_id):
    """Add item to cart in session."""
   
    # if comic is in db, query the db and return comic
    # else query api and return comic object

    # check for comic issue in SQL db
    exists = db.session.query(db.exists().where(Comic.id == comic_id)).scalar()
    
    if exists:
        # query SQL db comic
        comic = Comic.query.get(comic_id)
    else:
        # query api for comic, returns comic object instance
        new_comic = get_comic_issue(comic_id)

        # add the comic to the db if it does not already exist, returns db comic object
        comic = add_comic_to_db(new_comic)

    # check for the cart in the session
    if 'cart' in session:
        
        # item is not in the session cart, add it
        if not any(comic.name in d for d in session['cart']):
            # use the comic.name as the key and the quantity as the value
            session['cart'].append({'id': comic.id, comic.name: 1})
            # update the session
            session.modified = True

        # item was in the session cart, update the quantity
        elif any(comic.name in d for d in session['cart']):
            for d in session['cart']:
                # increment the quantity of the item by 1
                d.update((k, v+1) for k, v in d.items() if k == comic.name)
            # update the session
            session.modified = True

    # cart was not in the session
    else:
        # create the session cart with the comic being added
        # comic name is the key and the quantity in the cart is the value
        session['cart'] = [{'id': comic.id, comic.name: 1}]
        # update the session
        session.modified = True

    # stay on the comic details page
    return redirect('/cart')



@app.route('/cart/update')
def edit_cart_contents():
    """Remove item from cart in session."""
    # dictionary to hold the quantities from the query params
    quantities = {}
    # get the query params (quantity inputs from cart items)
    args = request.args
    # if parameters were passed
    if args:
        # iterate over the k,v pairs and add them to the quantities dict
        for key, value in args.items():
            quantities.update({key:value})
        # iterate over cart in session
        for d in session['cart']:
            # get the comic from the db
            comic = Comic.query.get(d['id'])
            # update the item quantity value if the key matches the comic.name
            d.update((k, quantities[str(d['id'])]) for k, v in d.items() if k == comic.name)
        # update the session
        session.modified = True 
    # redirect to cart (price information will be updated in the /cart route)
    return redirect('/cart')


@app.route('/cart/remove/<int:comic_id>')
def remove_cart_item(comic_id):
    """Remove item from cart in session."""
    
    for i in range(len(session['cart'])):
        # remove the item matching the comid_id in the session
        if session['cart'][i]['id'] == comic_id:
            del session['cart'][i]
            session.modified = True
            # exit the loop after the item has been removed
            break
    return redirect('/cart')

@app.route("/cart/clear")
def clear_cart_contents():
    # pop each item from the session cart until the session['cart'] length is 0
    clear_session_cart()

    return redirect("/cart")

#******************************************Checkout Routes***************************************

@app.route('/checkout/create-session', methods=["GET","POST"])
def create_checkout_session():
    """Create checkout session"""
    items_list = []
    success_url = 'http://127.0.0.1:5000/checkout/success?session_id={CHECKOUT_SESSION_ID}'
    cancel_url = 'http://127.0.0.1:5000/checkout/cancel'


    for d in session['cart']:

        comic = Comic.query.get(d['id'])

        new_product = stripe.Product.create(
            name=comic.name,
            default_price_data={
                "unit_amount": 499,
                "currency": "usd",
                "recurring": None,
            },
            expand=["default_price"]
        )


        item={}
        item["price"] = new_product["default_price"]["id"]
        item["quantity"] = d[comic.name]

        items_list.append(dict(item))

    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=items_list,
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
        )
     

    except Exception as e:
        return str(e)


    return redirect(checkout_session.url, code=303)
    

@app.route('/checkout/success')
def show_checkout_success():
    """Show success message and clear the session cart."""

    # grab the session id from the url
    args = request.args.get('session_id')
    # get the stripe checkout session object
    checkout_session = stripe.checkout.Session.retrieve(args)

    # total from stripe api is str ->
    # coerce api total to float -> divide by 100 to format as curreny amount with 2 decimal places ->
    # coerce back to str to add to db column 'total'
    checkout_total = str(float(checkout_session['amount_total']/100))
    
    # create a new order instance
    new_order = Order(session_id=checkout_session['id'],
                  sub_total=checkout_session['amount_subtotal'],
                  total=checkout_total,
                  customer_name=checkout_session['customer_details']['name'],
                  phone=checkout_session['customer_details']['phone'],
                  email=checkout_session['customer_details']['email']
                  )

    # add and commit the new order to db
    db.session.add(new_order)
    db.session.commit()

    # query the order from the db
    order = Order.query.get(new_order.id)
    
    # loop over items in session cart
    for d in session['cart']:
        # query the comic
        comic = Comic.query.get(d['id'])
        # append the comic to order.itmes list
        order.items.append(comic)

    # commit to db
    db.session.commit()

    # check for logged in user
    if g.user:
        # query the user from the db
        user = User.query.get(g.user.id)
        # append the order to the user.orders list
        user.orders.append(order)
        # commit to db
        db.session.commit()

        # clear the session cart
        clear_session_cart()

        return render_template("success.html", user=user)

    else:
        # clear the session cart
        clear_session_cart()

        return render_template("success.html")


@app.route('/checkout/cancel')
def show_checkout_cancel():
    """Show cancel checkout page"""
    return render_template("cancel.html")


#******************************************Comic Routes***************************************

@app.route('/comic/<int:comic_id>')
def show_comic_details(comic_id):
    """Show comic product page."""
    comic = get_comic_issue(comic_id)

    return render_template('comic-details.html', comic=comic)

@app.route("/user/order/<int:order_id>")
def show_order_details(order_id):
    """Show order details page."""

    order = Order.query.get(order_id)
    order_items = order.items

    return render_template("order-details.html", order=order, order_items=order_items)