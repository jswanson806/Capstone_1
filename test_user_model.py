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
from sqlalchemy import exc


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
        uid1 = 1111
        self.testuser.id = uid1

        self.user1 = User.signup("test1", "user1", "testuser1", "test1@test.com", "testuser1")
        uid2 = 2222
        self.user1.id = uid2

        db.session.commit()


    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp


    def test_valid_signup(self):
        """Can we sign up a user using the user model?"""

        u_test = User.signup("test2", "user2", "testuser2", "testuser2@test.com", "password")
        uid = 3333
        u_test.id = uid
        db.session.commit()

        u_test = User.query.get(uid)
        self.assertIsNotNone(u_test)

        self.assertEqual(u_test.first_name, "test2")
        self.assertEqual(u_test.last_name, "user2")
        self.assertEqual(u_test.username, "testuser2")
        self.assertEqual(u_test.email, "testuser2@test.com")
        self.assertNotEqual(u_test.password, "password")
        self.assertTrue(u_test.password.startswith("$2b$"))


    def test_invalid_email_signup(self):
        """Test for invalid email entry"""

        invalid = User.signup("test3", "user3", "testuser3", None, "password")
        uid = 4444
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()


    def test_invalid_username_signup(self):
        """Test for invalid username entry"""

        invalid = User.signup("test3", "user3", None, "testuser3@email.com", "password")
        uid = 5555
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()


    def test_invalid_passwword_signup(self):
        """Test for invalid password entry"""

        with self.assertRaises(ValueError) as context:
            User.signup("test4", "user4", 'testuser4', 'testuser4@email.com', "")

        with self.assertRaises(ValueError) as context:
            User.signup("test4", "user4", 'testuser4', 'testuser4@email.com', None)


    def test_valid_auth(self):
        """Test for valid authorization"""

        u = User.authenticate(self.testuser.username, "password")
        self.assertIsNotNone(u)
        u1 = User.query.get(self.testuser.id)
        self.assertEqual(u1.id, 1111)


    def test_invalid_username(self):
        """Test for wrong username"""
        
        self.assertFalse(User.authenticate("notthisname", "password"))


    def test_wrong_password(self):
        """Test for wrong password"""

        self.assertFalse(User.authenticate(self.testuser.username, "notthisone"))