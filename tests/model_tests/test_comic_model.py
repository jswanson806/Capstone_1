import os
from unittest import TestCase
import collections.abc
collections.Container = collections.abc.Container
collections.Mapping = collections.abc.Mapping
collections.MutableMapping = collections.abc.MutableMapping
collections.Iterable = collections.abc.Iterable
collections.MutableSet = collections.abc.MutableSet
collections.Callable = collections.abc.Callable
from models import db, Comic


os.environ['DATABASE_URL'] = "postgresql:///comicbook_store"


from app import app

db.create_all()

app.config["WTF_CSRF_ENABLED"] = False

class UserViewTestCase(TestCase):
    """Test views for logged in users"""

    def setUp(self):
        """Create test client, add sample data."""

        Comic.query.delete()
        
        self.client = app.test_client()

        # test comics
        self.test_comic = Comic(id="8888",
                            name="testcomic",
                            issue_number="8888",
                            deck="this is a test comic")

        self.comic1 = Comic(id="9999",
                        name="testcomic1",
                        issue_number="9999",
                        deck="this is another test comic")

        
        db.session.commit()


    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp


    def test_add_new_comic(self):
        """Does the comic model work?"""

        comic2 = Comic(id='7777', 
                        name='testcomic2',
                        issue_number='0002',
                        deck='this is a test deck',
                        price='4.99',
                        cover_img='test image url')
        
        db.session.add(comic2)
        db.session.commit()

        # is the comic added to the db?
        comic = Comic.query.get(7777)
        self.assertIsNotNone(comic)

        # does the comic have the correct information?
        self.assertEqual(comic.id, 7777)
        self.assertEqual(comic.name, 'testcomic2')
        self.assertEqual(comic.issue_number, '0002')
        self.assertEqual(comic.deck, 'this is a test deck')
        self.assertEqual(comic.price, '4.99')
        self.assertEqual(comic.cover_img, 'test image url')