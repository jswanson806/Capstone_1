from secret import COMIC_API_KEY
import requests
from models import db, Comic, Character

# API URLs
COMIC_BASE = 'https://comicvine.gamespot.com/api'
COMIC_CHARACTERS = 'https://comicvine.gamespot.com/api/characters'
COMIC_CHARACTER = 'https://comicvine.gamespot.com/api/character/4005-'
COMIC_ISSUE = 'https://comicvine.gamespot.com/api/issue/4000-'


    
#*****************************API Methods******************************


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


        for i in data['results']['character_credits']:
            # check for character in SQL db
            exists = db.session.query(db.exists().where(Character.id == i.get('id'))).scalar()
            
            if exists:
                character = Character.query.get(i.get('id'))
                character.appearances.append(new_comic)

        db.session.add(new_comic)
        db.session.commit()

        return new_comic


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
            publisher_id = data['results'][i]['publisher']['id'] or None
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
