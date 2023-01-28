import os
import requests
from models import db, Comic, Character, Order
from flask import session
import stripe

COMIC_API_KEY = os.environ.get('COMIC_API_KEY','6097d6aeb080923e8927570f0ff9ac6f3292fe0a')
stripe.api_key = os.environ.get('STRIPE_TEST_API_KEY', 'sk_test_51MNeg0DugXxFxym6nqUpiTKKtRpdLwRjM4Hix8NKPObBVtDYIVuW8FxTbLipSvxvt4Oj45yjeUe2iFUTTLVrdadF00KclEHSAC')

# API URLs
COMIC_BASE = 'https://comicvine.gamespot.com/api'
COMIC_CHARACTERS = 'https://comicvine.gamespot.com/api/characters'
COMIC_CHARACTER = 'https://comicvine.gamespot.com/api/character/4005-'
COMIC_ISSUE = 'https://comicvine.gamespot.com/api/issue/4000-'


    
#*****************************API Methods******************************


def get_comic_issue(comic_id):
    """
    >>> If comic exists in db, query the db
    >>> returns comic object
    >>>
    >>> Else query the comic API and create a new instance of Comic
    >>> returns comic object
    """

    key = COMIC_API_KEY
    url = COMIC_ISSUE + f'{comic_id}'
    params = {"api_key":key, 
              "field_list":"id,name,deck,cover_date,issue_number,image,first_appearance_characters,character_credits",
              "format":"json"
             }
    headers = {
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
              "Content-Type": "application/json"
              }
    try:
        res = requests.get(url, headers=headers, params=params)
        res.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        return "An Http Error occurred:" + repr(errh)
    except requests.exceptions.ConnectionError as errc:
        return "An Error Connecting to the API occurred:" + repr(errc)
    except requests.exceptions.Timeout as errt:
        return "A Timeout Error occurred:" + repr(errt)
    except requests.exceptions.RequestException as err:
        return "An Unknown Error occurred" + repr(err)
    
    data = res.json()

    return data


def add_comic_to_db(comic):
    """Add the comic to the db
    >>> returns comic instance
    """

    db.session.add(comic)
    db.session.commit()

    new_comic = Comic.query.get(comic.id)

    return new_comic


def find_single_character(character_id):
    """
    >>> Query the API for the comic character
    >>> returns json response data
    
    """

    key = COMIC_API_KEY
    url = COMIC_CHARACTER + f'{character_id}'

    params = {"api_key":key, 
              "field_list":"id,name,real_name,aliases,deck,first_appeared_in_issue,count_of_issue_appearances,image,api_detail_url,publisher,issue_credits",
              "format":"json"
            }

    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    "Content-Type": "application/json"
    }

    try:
        res = requests.get(url, headers=headers, params=params)
        res.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        return "An Http Error occurred:" + repr(errh)
    except requests.exceptions.ConnectionError as errc:
        return "An Error Connecting to the API occurred:" + repr(errc)
    except requests.exceptions.Timeout as errt:
        return "A Timeout Error occurred:" + repr(errt)
    except requests.exceptions.RequestException as err:
        return "An Unknown Error occurred" + repr(err)
    
    data = res.json()

    return data


def find_character_appearances(character_id):
    """
    >>> Query the API for the comic character
    >>> returns json response data
    
    """

    key = COMIC_API_KEY
    url = COMIC_CHARACTER + f'{character_id}'

    params = {"api_key":key, 
              "field_list":"id,name,real_name,aliases,deck,first_appeared_in_issue,count_of_issue_appearances,image,api_detail_url,publisher,issue_credits",
              "format":"json"
            }

    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    "Content-Type": "application/json"
    }

    try:
        res = requests.get(url, headers=headers, params=params)
        res.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        return "An Http Error occurred:" + repr(errh)
    except requests.exceptions.ConnectionError as errc:
        return "An Error Connecting to the API occurred:" + repr(errc)
    except requests.exceptions.Timeout as errt:
        return "A Timeout Error occurred:" + repr(errt)
    except requests.exceptions.RequestException as err:
        return "An Unknown Error occurred" + repr(err)
    
    data = res.json()

    return data


def get_and_filter_appearances(data):
    # list to hold character appearances
    appearances = []

    # title names to ignore
    forbidden_names = ['TPB','HC','HC/TPB', 'TPB/HC', 'HC\TPB', 'TPB\HC', 'Chapter','Volume', '', 'SC']

    # shorthand variable for data results
    results = data['results']

    # shorthand variable for dictionary of comics where character appears
    comic_credits = results['issue_credits']
    
    # loop over all of the comics in response data
    for i in comic_credits:
        # additional title filters within the loop for titles that start with forbidden names
        if i['name'] not in forbidden_names and i['name'] != None and not i['name'].startswith(('Volume', 'Chapter', 'Book', 'Part', 'Vol.')):
            id = i['id']
            name = i['name']
            comic = {'id': id, 'name': name}
            # append issues to appearances list
            appearances.append(comic)
            
    db.session.commit()

    return appearances


def add_character_to_db(character):
    """Add the character to the db
    >>> returns character instance
    """

    db.session.add(character)
    db.session.commit()

    new_character = Character.query.get(character.id)

    return new_character


def search_characters(search_term):
    """
    Returns characters with similar names to the search_term.

    """

    # query the API
    # -> iterate over response data and add characters to the database
    # -> return the list of characters from the API


    key = COMIC_API_KEY
    url = COMIC_CHARACTERS      
    
    params = {"api_key":key, 
                   "field_list":"id,name,real_name,aliases,deck,first_appeared_in_issue,count_of_issue_appearances,image,api_detail_url,publisher",
                   "filter":f"name:{search_term}",
                   "format":"json"
                   }
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    "Content-Type": "application/json"
    }

    try:
        res = requests.get(url, headers=headers, params=params)
        res.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        return "An Http Error occurred:" + repr(errh)
    except requests.exceptions.ConnectionError as errc:
        return "An Error Connecting to the API occurred:" + repr(errc)
    except requests.exceptions.Timeout as errt:
        return "A Timeout Error occurred:" + repr(errt)
    except requests.exceptions.RequestException as err:
        return "An Unknown Error occurred" + repr(err)
    
    data = res.json() 

    return data


def handle_search_results(data):
    search_results = []
    # count of returned characters from api search
    results_count = data['number_of_page_results']
    # iterate over data and extract character information

    # handle possible NoneType from response data
    for i in range (0, results_count):
        result = data['results'][i]

        id = result['id']
        name = result['name']
        
        if result['real_name'] != None:
            real_name = result['real_name']
        else:
            real_name = None

        if result['deck'] != None:
            deck = result['deck']
        else:
            deck = None

        if result['first_appeared_in_issue'] != None:
            first_appear_issue_id = result['first_appeared_in_issue']['id']
        else:
            first_appear_issue_id = None

        if result['first_appeared_in_issue'] != None:
            first_appear_issue_num = result['first_appeared_in_issue']['issue_number']
        else:
            first_appear_issue_num = None

        if result['first_appeared_in_issue'] != None:
            first_appear_issue_name = result['first_appeared_in_issue']['name']
        else: 
            first_appear_issue_name = None

        if result['count_of_issue_appearances'] != None:
            total_appearances = result['count_of_issue_appearances']
        else:
            total_appearances = None

        if result['image'] != None:
            
            if result['image']['icon_url'] != None:
                icon_image_url = result['image']['icon_url']
            else:
                icon_image_url = None

            if result['image']['original_url'] != None:
                original_url = result['image']['original_url']
            else:
                original_url = None

        if result['publisher'] != None:

            if result['publisher']['id'] != None:
                publisher_id = result['publisher']['id']
            else:
                publisher_id = None

            if result['publisher']['name'] != None:
                publisher_name = result['publisher']['name']
            else:
                publisher_name = None


        # create new character instance
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
        # append transient character object to the search_results list
        search_results.append(new_character)

    return search_results


def clear_session_cart():
    i = 0
    while i < len(session['cart']):
        session['cart'].pop(i)

    session.modified = True
    return None
    

def get_all_stripe_products():

    product_list = stripe.Product.list()

    return product_list


def create_stripe_product(comic_name):

    new_product = stripe.Product.create(
            name=comic_name,
            default_price_data={
                "unit_amount": 499,
                "currency": "usd",
                "recurring": None,
            },
            expand=["default_price"]
        )

    return new_product


def create_line_items():
    """Retrieves products list from stripe inventory
    >>> iterates over items in session cart
    >>> queries comics from local db
    >>> finds comics in stripe inventory and retrieves their default price id
    >>> if comic not in inventory ->
    >>> creates a new stripe product and retrieves the default price id
    >>>
    >>> builds a dictionary of each item with product name, price and quantity
    >>> dictionary items are appended to items_list and returned
    """
    # empty list to hold the dictionary of items to pass to the stripe checkout session line_items
    items_list = []

    # return a list of products in stripe inventory
    products_list = get_all_stripe_products()

    # iterate over items in session cart
    for d in session['cart']:
        # empty dict to hold line items
        item={}

        # get the comic in session cart from db
        comic = Comic.query.get(d['id'])

        # iterate over dictionaries of products in stripe inventory
        for i in products_list:
        # check for the comic in the stripe inventory

            if comic.name in i.values():
                # if the product is already in stripe inventory, get the default price id
                prod_price = i['default_price']
                # set key 'price' in item dict to the default price id for the stripe product
                item["price"] = prod_price
                # stop the loop and move on the next product
                break

            # else, product is not in products list
            else:
                # create a new product in stripe inventory
                new_product = create_stripe_product(comic.name)
                # set the key 'price' to the default price id from the stripe product
                item["price"] = new_product['default_price']["id"]
                # stop the loop and move on the next product
                break

        # set the key quantity in item dict to the item quantity from session cart
        item["quantity"] = d[comic.name]
        # append the dictionary to the items_list
        items_list.append(dict(item))
    
    return items_list


def create_checkout_sess(items_list):
    """Creates a stripe checkout session
    >>> uses items_list to pass price and quantity information
    >>> returns a checkout_session object
    """
    success_url = 'http://127.0.0.1:5000/checkout/success?session_id={CHECKOUT_SESSION_ID}'
    cancel_url = 'http://127.0.0.1:5000/checkout/cancel'
    
    try:
        # create a new stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            # pass in the list of dicts of each item price and quantity in the cart
            line_items=items_list,
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
        )
    except Exception as e:
        return str(e)

    return checkout_session

def create_new_order(args):
    """Creates a new order in the local db
    >>> retrieves the checkout session
    >>> formats the checkout total to 2 decimal places
    >>> creates an order object instance, saves and commits
    >>> 
    >>> query the order from the db
    >>> loops over items in session cart, queries the comic object ->
    >>> appends the comic objects to order.items
    >>> returns the order object
    """
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

    return order