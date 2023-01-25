import os
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