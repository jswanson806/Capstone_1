    
import os
from unittest import TestCase
import collections.abc
collections.Container = collections.abc.Container
collections.Mapping = collections.abc.Mapping
collections.MutableMapping = collections.abc.MutableMapping
collections.Iterable = collections.abc.Iterable
collections.MutableSet = collections.abc.MutableSet
collections.Callable = collections.abc.Callable
from models import db, User, Comic, Character, Comic, Order
from bs4 import BeautifulSoup

os.environ['DATABASE_URL'] = "postgresql:///comicbook_store"

from app import app, CURR_USER_KEY

db.create_all()

app.config["WTF_CSRF_ENABLED"] = False


class UserViewTestCase(TestCase):
    """Test views for logged in users"""


    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Order.query.delete()
        
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


    def setup_orders(self):
        # test orders
        test_order = Order(session_id="2222",
                            sub_total="499",
                            total="4.99",
                            customer_name="test user",
                            email="test@test.com")
        order1 = Order(session_id="3333",
                            sub_total="899",
                            total="8.99",
                            customer_name="test user",
                            email="test@test.com")
        db.session.add_all([test_order, order1])
        db.session.commit()

    def test_order_add_to_database(self):
        """Are orders being added to the database?"""

        self.setup_orders()

        order = Order.query.filter(Order.session_id=='2222').all()
        self.assertIsNotNone(order)

        order1 = Order.query.filter(Order.session_id=='3333').all()
        self.assertIsNotNone(order1)


    def test_order_history_display(self):
        """Can we see orders made by the user?"""
        self.setup_orders()

        # fake login
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            # first order from db
            order = Order.query.filter(Order.session_id == '2222').one()
            
            # request first order
            resp = c.get(f'/user/{self.testuser.id}/order/{order.id}')
            self.assertEqual(resp.status_code, 200)

            # check for first order total
            self.assertIn("4.99", str(resp.data))

            # second order from db
            order1 = Order.query.filter(Order.session_id == '3333').one()

            # request second order
            resp = c.get(f'/user/{self.testuser.id}/order/{order1.id}')
            self.assertEqual(resp.status_code, 200)

            # check for first order total
            self.assertIn("8.99", str(resp.data))

    def test_order_history_unauthorized(self):
        """Are users prevented from seeing other users order history?"""

        self.setup_orders()

        # wrong user variable
        user = User.query.filter(User.first_name=='test1').one()
        # order to try and view
        order = Order.query.filter(Order.session_id=='2222').one()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # request character list from wrong user
            resp = c.get(f'/user/{user.id}/order/{order.id}', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            # check for flash message
            self.assertIn('Access Unauthorized', str(resp.data))