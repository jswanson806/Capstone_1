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

    # check for comic issue in SQL db
    exists = db.session.query(db.exists().where(Comic.id == comic_id)).scalar()
    
    if exists:
        # query SQL db comic
        comic = Comic.query.get(comic_id)  
        return comic
    
    else:
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

        res = requests.get(url, headers=headers, params=params)

        data = res.json()

        new_comic = Comic(id = data['results']['id'],
                        name = data['results']['name'],
                        issue_number = data['results']['issue_number'],
                        cover_date = data['results']['cover_date'],
                        cover_img = data['results']['image']['original_url'],
                        deck = data['results']['deck']
                        )

        return new_comic


def add_comic_to_db(comic):

    # check for comic issue in SQL db
    exists = db.session.query(db.exists().where(Comic.id == comic.id)).scalar()
    
    # comic exists in db, return None
    if exists:
        return None

    # comic is not in the db, add and commit, return None
    else:
        db.session.add(comic)
        db.session.commit()

        return None



def get_character_appearances(character_id):
    key = COMIC_API_KEY
    url = COMIC_CHARACTER + f'{character_id}'
    appearances = []


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
            appearances.append(issue)
    
    return appearances

def search_characters(search_term):
    """
    Returns characters with similar names to the search_term.

    Limits calls to the API:
    If characters do not exist in the SQL db already ->
    call the API and generate new character instances from the returned data ->
    Add the characters to the SQL db and return the list of character SQLAlchemy objects
    """

    

    # if no matching characters are found in SQL db, query the API
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

        if result['publisher']['id'] != None:
            publisher_id = result['publisher']['id']
        else:
            publisher_id = None

        if result['publisher']['name'] != None:
            publisher_name = result['publisher']['name']
        else:
            publisher_name = None

        # check for character in SQL db
        exists = db.session.query(db.exists().where(Character.id == id)).scalar()
        # if character is already present in SQL db, query the characters and append them to search_results
        if exists:
            character = Character.query.get(id)
            search_results.append(character)
        
        else:
            # if the character is not in the db already -> create new character instance
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

def clear_session_cart():
    i = 0
    while i < len(session['cart']):
        session['cart'].pop(i)

    session.modified = True
    return None
    