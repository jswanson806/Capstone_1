import os
import requests
from models import db, Comic, Character
from flask import session

COMIC_API_KEY = os.environ.get('COMIC_API_KEY','6097d6aeb080923e8927570f0ff9ac6f3292fe0a')

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
    new_comic = Comic(id = data['results']['id'],
                    name = data['results']['name'],
                    issue_number = data['results']['issue_number'],
                    cover_date = data['results']['cover_date'],
                    cover_img = data['results']['image']['original_url'],
                    deck = data['results']['deck'],
                    price = '4.99'
                    )

    return new_comic


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

    # shorthand variable for data results
    results = data['results']

    character = Character(id=results['id'],
                          name=results['name'], 
                          real_name=results['real_name'], 
                          deck=results['deck'], 
                          first_appear_issue_id=results['first_appeared_in_issue']['id'],
                          first_appear_issue_name=results['first_appeared_in_issue']['name'],
                          first_appear_issue_num=results['first_appeared_in_issue']['issue_number'],                 
                          total_appearances=results['count_of_issue_appearances'], 
                          icon_image_url=results['image']['icon_url'],
                          original_url=results['image']['original_url'],
                          publisher_id=results['publisher']['id'],
                          publisher_name=results['publisher']['name']
                          )

    return character

def find_character_appearances(character_id):
    """
    >>> Query the API for the comic character
    >>> returns json response data
    
    """

    # list to hold character appearances
    appearances = []

    # title names to ignore
    forbidden_names = ['TPB','HC','HC/TPB', 'TPB/HC', 'HC\TPB', 'TPB\HC', 'Chapter','Volume', '', 'SC']

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
    # count of returned characters from api search
    results_count = data['number_of_page_results']
    # iterate over data and extract character information

    # handle possible NoneType from response data
    for i in range (0,results_count):
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

            # append character SQLAlchemy object to the search_results list
            search_results.append(new_character)

    return search_results


def clear_session_cart():
    i = 0
    while i < len(session['cart']):
        session['cart'].pop(i)

    session.modified = True
    return None
    