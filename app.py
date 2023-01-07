
import os
from flask import Flask, jsonify, make_response, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User, Character, Comic, Review, Order, Transaction
from forms import UserSignUpForm, EditUserForm, LoginForm, UserSignInForm, ShippingAddressForm, BillingAddressForm
from methods import calculate_taxes, calculate_total, search_characters, get_character_appearances, get_comic_issue
from secret import STRIPE_TEST_API_KEY
import stripe

CURR_USER_KEY = "curr_user"
stripe.api_key = STRIPE_TEST_API_KEY

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
        
    return render_template('shop.html', user=user)


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

    user = User.query.get_or_404(user_id)
    
    form = EditUserForm(obj=user)

    if CURR_USER_KEY in session:
        if form.validate_on_submit():
            user.username=form.username.data
            user.first_name=form.first_name.data
            user.last_name=form.last_name.data
            user.mobile=form.mobile.data
            user.email=form.email.data
            user = User.authenticate(form.username.data, form.password.data)

            if user:
                db.session.commit()
                return redirect(f'/users/{user.id}/account')
            else:
                flash('Incorrect password')
                return redirect('/')

    return render_template('my-account.html', form=form)


@app.route('/users/<int:user_id>/reading')
def show_user_wishlist(user_id):
    """Show user reading list."""

    if g.user.id != user_id:
        flash("Access unauthorized", "danger")
        return redirect('/signin')

    reading_list = g.user.reading

    return render_template('reading-list.html', reading_list=reading_list)


@app.route('/users/reading_list/<int:comic_id>', methods=["POST"])
def add_reading_list_item(comic_id):
    """Add item to user wishlist."""

    if not g.user:
        flash("Login to save comics", "danger")
        return redirect('/')

    comic = Comic.query.get_or_404(comic_id)

    user = User.query.get(g.user.id)
    user.reading.append(comic)
    db.session.commit()

    return redirect(f'/comic/{comic.id}')


@app.route('/users/<int:comic_id>/remove_comic', methods=["POST"])
def remove_wishlist_item(comic_id):
    """Remove comic from user reading list."""

    if not g.user.id:
        flash("Access Unauthorized.", "danger")
        return redirect('/signin')
    
    comic = Comic.query.get_or_404(comic_id)
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
    """Add character to list of user's saved characters."""

    if not g.user:
        flash("Login to save characters.", "danger")
        return redirect('/signin')
    
    character = Character.query.get_or_404(character_id)

    user = User.query.get_or_404(g.user.id)

    user.characters.append(character)

    db.session.commit()

    return redirect(f'/characters/{character_id}')
    

@app.route('/users/<int:character_id>/remove_character', methods=["POST"])
def remove_character(character_id):
    """Remove character from list of user's saved characters."""

    if not g.user.id:
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
    # get matching results from api - limit 100
    args = request.args['prod-search']
    search_res = search_characters(args)
    
    return render_template('characters-search.html', characters=search_res)

@app.route('/characters/<int:character_id>')
def show_character_details(character_id):
    """Show single character details page."""
    character = Character.query.get_or_404(character_id)
    
    appearances = get_character_appearances(character_id)

    return render_template('character-details.html', character=character, appearances=appearances)

#***************************************Cart Routes***************************************

@app.route('/cart', methods=["GET"])
def show_session_cart():
    """Show contents of current cart in session."""
    cart_contents = []
    subtotal = 0

    for item in session['cart']:
        # get the comic from the database
        comic = Comic.query.get_or_404(item['id'])
        # coerce the item quantity and comic price to float -> multiply them by one another 
        # -> round the result to 2 decimals
        item_subtotal = round(float(item[comic.name]) * float(comic.price), 2)
        # append the comic to the cart_contents list
        cart_contents.append((comic, int(item[comic.name]), item_subtotal))
        # update the subtotal with the price of each comic in the session cart
        subtotal = round(subtotal + item_subtotal, 2)
    
    # calculate the tax amount based on the subtotal
    taxes = calculate_taxes(subtotal)
    # calculate the total
    total = calculate_total(taxes, subtotal)

    return render_template('cart.html', 
                            cart_contents=cart_contents, 
                            subtotal=subtotal, 
                            taxes=taxes, 
                            total=total)


@app.route('/cart/<int:comic_id>/add', methods=["POST"])
def update_session_cart(comic_id):
    """Add item to cart in session."""
   
    comic = Comic.query.get_or_404(comic_id)

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
            comic = Comic.query.get_or_404(d['id'])
            # update the item quantity value if the key matches the comic.name
            d.update((k, quantities[str(d['id'])]) for k, v in d.items() if k == comic.name)
        # update the session
        session.modified = True 
    # redirect to cart (price information will be updated in the /cart route)
    return redirect('/cart')


@app.route('/cart/remove/<int:comic_id>')
def remove_cart_item(comic_id):
    """Remove item from cart in session."""
    # loop 
    for i in range(len(session['cart'])):
        # 
        if session['cart'][i]['id'] == comic_id:
            del session['cart'][i]
            session.modified = True
            break
    return redirect('/cart')

@app.route("/cart/clear")
def clear_cart_contents():

    for i in range(len(session['cart'])):
        session['cart'].pop([i])
    session.modified = True

    return redirect("/cart")

#******************************************Checkout Routes***************************************

@app.route('/checkout/create-session', methods=["GET","POST"])
def create_checkout_session():
    """Create checkout session"""
    line_items_list = []

    for d in session['cart']:
        comic = Comic.query.get_or_404(d['id'])
        line_item={}
        line_item["price"] = 'price_1MNfjXDugXxFxym65oPw8FJx'
        line_item["quantity"] = d[comic.name]

        line_items_list.append(dict(line_item))

    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=line_items_list,
            mode='payment',
            success_url='http://127.0.0.1:5000/checkout/success',
            cancel_url='http://127.0.0.1:5000/checkout/cancel',
        )
    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)

@app.route('/checkout/success')
def show_checkout_success():
    """Create checkout session"""
    return render_template("success.html")

@app.route('/checkout/cancel')
def show_checkout_cancel():
    """Create checkout session"""
    return render_template("cancel.html")

#******************************************Comic Routes***************************************

@app.route('/comic/<int:comic_id>')
def show_comic_details(comic_id):
    """Show comic product page."""
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

