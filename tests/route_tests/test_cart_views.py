import os
import flask
from unittest import TestCase
import collections.abc
collections.Container = collections.abc.Container
collections.Mapping = collections.abc.Mapping
collections.MutableMapping = collections.abc.MutableMapping
collections.Iterable = collections.abc.Iterable
collections.MutableSet = collections.abc.MutableSet
collections.Callable = collections.abc.Callable
from models import db, User, Comic

os.environ['DATABASE_URL'] = "postgresql:///comicbook_store"


from app import app, CURR_USER_KEY

db.create_all()

app.config["WTF_CSRF_ENABLED"] = False

class UserViewTestCase(TestCase):
    """Test views for logged in users"""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Comic.query.delete()
        
        self.client = app.test_client()

        # test users
        self.testuser = User.signup(first_name="test",
                                    last_name="user",
                                    username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    )
        self.user1 = User.signup("test1", "user1", "testuser1", "test1@test.com", "testuser1")

        

        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp


    def setup_comics(self):
        # test comics
        test_comic = Comic(id="8888",
                            name="testcomic",
                            issue_number="8888",
                            deck="this is a test comic")
                            
        comic1 = Comic(id="9999",
                        name="testcomic1",
                        issue_number="9999",
                        deck="this is another test comic")

        db.session.add_all([test_comic, comic1])
        db.session.commit()


    def test_add_to_cart(self):
        """Can we add items to the cart?"""
        # setup test comics in db
        self.setup_comics()
        # real comic id from api
        comic_id = 964800

        
        with self.client as c:
            
            # adding comic from the database
            resp = c.post('/cart/8888/add', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            # adding comic from the api
            resp = c.post(f'/cart/{comic_id}/add', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            # did the comic get added to the db after calling from api?
            new_comic = Comic.query.get(comic_id)
            self.assertIsNotNone(new_comic)

            # are the comics being added to the session cart?
            self.assertEqual(2, len(flask.session['cart']))

            # are the comics being added to cart in proper format?
            self.assertEqual(flask.session['cart'], [{'id': 8888, 'testcomic': 1}, {'id': 964800, 'Power Vacuum, Part 4: The Leap': 1}])


    def test_add_duplicate_to_cart(self):
        """Can we update the cart quantities by adding duplicate item?"""
        # setup test comics in db
        self.setup_comics()

        with self.client as c:
            
            # adding comic from the database
            resp = c.post('/cart/8888/add', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            # adding duplicate of comic
            resp = c.post('/cart/8888/add', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            # is there only one comic with id 8888 in db?
            new_comic = Comic.query.filter(Comic.id==8888).one()
            self.assertIsNotNone(new_comic)

            # is the quantity of the comic in session cart updated to 2?
            self.assertEqual(flask.session['cart'], [{'id': 8888, 'testcomic': 2}])


    def test_update_cart_quantities(self):
        """Can we add items to the cart?"""
        # setup test comics in db
        self.setup_comics()

        with self.client as c:
            
            # adding comic from the database
            resp = c.post('/cart/8888/add', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            # adding duplicate of comic
            resp = c.post('/cart/8888/add', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            # is the quantity of the comic in session cart == 2?
            self.assertEqual(flask.session['cart'], [{'id': 8888, 'testcomic': 2}])

            # request to update item quantity in session cart to == 1
            resp = c.get('/cart/update', query_string={8888: 1})

            # is the quantity of the comic in session cart == 1?
            self.assertEqual(flask.session['cart'], [{'id': 8888, 'testcomic': '1'}])
            
            # make sure we did not add a duplicate item -> session['cart] length still == 1
            self.assertEqual(1, len(flask.session['cart']))


    def test_remove_from_cart(self):
        """Can we add items to the cart?"""
        # setup test comics in db
        self.setup_comics()

        with self.client as c:
            
            # adding comic from the database
            resp = c.post('/cart/8888/add', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            # adding duplicate of comic
            resp = c.post('/cart/9999/add', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            # check session['cart'] length -> expecting len == 2
            self.assertEqual(2, len(flask.session['cart']))

            # request to remove item from session cart
            resp = c.get('/cart/remove/8888', follow_redirects=True)

            # check session['cart'] length -> expecting len == 1
            self.assertEqual(1, len(flask.session['cart']))


    def test_clear_cart(self):
        """Does the clear_session_cart() method work?"""
        # setup test comics in db
        self.setup_comics()

        with self.client as c:
            
            # adding comic from the database
            resp = c.post('/cart/8888/add', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            # adding duplicate of comic
            resp = c.post('/cart/9999/add', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            # check session['cart'] length -> expecting len == 2
            self.assertEqual(2, len(flask.session['cart']))

            # request to clear session cart
            resp = c.get('/cart/clear', follow_redirects=True)

            # check session['cart'] length -> expecting len == 0
            self.assertEqual(0, len(flask.session['cart']))




    
