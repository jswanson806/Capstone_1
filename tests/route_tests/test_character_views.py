import os
from unittest import TestCase
import collections.abc
collections.Container = collections.abc.Container
collections.Mapping = collections.abc.Mapping
collections.MutableMapping = collections.abc.MutableMapping
collections.Iterable = collections.abc.Iterable
collections.MutableSet = collections.abc.MutableSet
collections.Callable = collections.abc.Callable
from models import db
from bs4 import BeautifulSoup

os.environ['DATABASE_URL'] = "postgresql:///comicbook_store"

from app import app, CURR_USER_KEY

db.create_all()

app.config["WTF_CSRF_ENABLED"] = False

class UserViewTestCase(TestCase):
    """Test views for logged in users"""

    def setUp(self):
        """Create test client"""

        self.client = app.test_client()


    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp


    def test_characters_search(self):
        """Do we return the correct search results from the api?"""
        with self.client as c:
            # search term
            search_term = 'Raven'

            resp = c.get(f'/characters?prod-search={search_term}')
            self.assertEqual(resp.status_code, 200)

            # instantiate beautiful soup
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            # find all td with class product-title
            found = soup.find_all("td", {"class": "product-title"})
            # did the api return 100 results?
            self.assertEqual(len(found), 100)
            # check first result
            self.assertEqual('Kraven the Hunter', found[0].text)
            # check second result
            self.assertEqual('Edgar Allan Raven', found[1].text)
            # check third result
            self.assertEqual('Raven', found[2].text)


    def test_show_character_details(self):
        """Can we see correct character details?"""
        with self.client as c:
            # character_id for 'Raven' from api
            character_id = 3584
            
            resp = c.get(f'/characters/{character_id}')
            self.assertEqual(resp.status_code, 200)
            # name display
            self.assertIn('Raven', str(resp.data))
            # first appearance display
            self.assertIn('Between Friend and Foe; Where Nightmares Begin; Whatever Happened to Sargon the Sorcerer #26', str(resp.data))

    def test_show_character_appearances(self):
        """Can we get character details?"""
        with self.client as c:
            # character_id for 'Raven' from api
            character_id = 3584
            
            resp = c.get(f'/characters/{character_id}')
            self.assertEqual(resp.status_code, 200)
            # name display
            # instantiate beautiful soup
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            # find all td with class product-title
            found = soup.find_all("li", {"class": "comic-appearance"})
            
            self.assertGreater(len(found), 0, "Length of found is not greater than 0")

