    
import os
from unittest import TestCase
import collections.abc
collections.Container = collections.abc.Container
collections.Mapping = collections.abc.Mapping
collections.MutableMapping = collections.abc.MutableMapping
collections.Iterable = collections.abc.Iterable
collections.MutableSet = collections.abc.MutableSet
collections.Callable = collections.abc.Callable
from models import db, User, Comic, Reading_List, Character, Character_List

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
        Character.query.delete()
        
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
                            customer_name="test1 user1",
                            email="test1@test.com")
        db.session.add_all([test_order, order1])
        db.session.commit()


    # def test_order_history_display(self):
    #     """Can we see orders made by the user?"""
    #     self.setup_orders()

    #     # fake login
    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.testuser.id

    #         resp = c.get(f'/users/{self.testuser.id}/account')
    #         self.assertEqual(resp.status_code, 200)

    #         # instantiate instance of BeautifulSoup
    #         soup = BeautifulSoup(str(resp.data), 'html.parser')
    #         # find all stat li's in HTML
    #         found = soup.find_all("td", {'id': "order-info"})
    #         print('###################', found)
    #         self.assertIn("#1", found[0].text)