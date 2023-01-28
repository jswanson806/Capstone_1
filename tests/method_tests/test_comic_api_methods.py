import json
import os
import collections.abc
collections.Container = collections.abc.Container
collections.Mapping = collections.abc.Mapping
collections.MutableMapping = collections.abc.MutableMapping
collections.Iterable = collections.abc.Iterable
collections.MutableSet = collections.abc.MutableSet
collections.Callable = collections.abc.Callable

from unittest import TestCase
from unittest.mock import patch, MagicMock
from models import db
from methods import get_comic_issue, find_single_character, find_character_appearances, get_and_filter_appearances, handle_search_results
from tests.test_character_data import *

os.environ['DATABASE_URL'] = "postgresql:///comicbook_store"

from app import app

db.create_all()

app.config["WTF_CSRF_ENABLED"] = False

class CheckoutTestClass(TestCase):

    @patch('methods.requests')
    def test_get_comic_issue(self, mock_requests):
        
        # set var mock_response to be instance of MagicMock()
        mock_response = MagicMock()
        # mock response status code
        mock_response.status_code = 200
        # mock json dictionary to be returned by the response object
        mock_response.json.return_value = test_comic_data
        
        # the get attr is a function, need return val attr
        # mock_requests is an instance of the MagicMock class (set above)

        # get function of requests library returns an instance of the response class, 
        # need to mock response object as var mock_response
        mock_requests.get.return_value = mock_response

        # check for the correst return value from mock_response
        self.assertEqual(get_comic_issue(123456789), test_comic_data)

    @patch('methods.requests')
    def test_find_single_character(self, mock_requests):

        # set var mock_response to be instance of MagicMock()
        mock_response = MagicMock()
        # mock response status code
        mock_response.status_code = 200
        # mock json dictionary to be returned by the response object
        mock_response.json.return_value = test_character_data
        
        # the get attr is a function, need return val attr
        # mock_requests is an instance of the MagicMock class (set above)

        # get function of requests library returns an instance of the response class, 
        # need to mock response object as var mock_response
        mock_requests.get.return_value = mock_response

        # check for the correst return value from mock_response
        self.assertEqual(find_single_character(987654321), test_character_data)
        

    @patch('methods.requests')
    def test_find_character_appearances(self, mock_requests):

        # set var mock_response to be instance of MagicMock()
        mock_response = MagicMock()
        # mock response status code
        mock_response.status_code = 200
        # mock json dictionary to be returned by the response object
        mock_response.json.return_value = test_issue_credit_data
        
        # the get attr is a function, need return val attr
        # mock_requests is an instance of the MagicMock class (set above)

        # get function of requests library returns an instance of the response class, 
        # need to mock response object as var mock_response
        mock_requests.get.return_value = mock_response

        # check for the correst return value from mock_response
        self.assertEqual(find_character_appearances(1928376450), test_issue_credit_data)



    def test_get_and_filter_appearances(self):
        """Testing the get and filter appearances method"""


        appearances = get_and_filter_appearances(test_filter_appearance_data)
        # are we filtering out the forbidden names?
        # assert list length to be 2
        self.assertEqual(len(appearances), 2)

        # check for dictionaries in returned list of appearances containing approved names
        self.assertEqual(get_and_filter_appearances(test_filter_appearance_data), [
                                {
                                    'id': 33333333333333,
                                    'name': 'test_appearance'
                                },
                                {
                                    'id': 44444444444444,
                                    'name': 'test_appearance1'
                                }
                            ]
                        )


    @patch('methods.requests')
    def test_search_characters(self, mock_requests):

        # set var mock_response to be instance of MagicMock()
        mock_response = MagicMock()
        # mock response status code
        mock_response.status_code = 200
        # mock json dictionary to be returned by the response object
        mock_response.json.return_value = test_search_data
            
        
        # the get attr is a function, need return val attr
        # mock_requests is an instance of the MagicMock class (set above)

        # get function of requests library returns an instance of the response class, 
        # need to mock response object as var mock_response
        mock_requests.get.return_value = mock_response

        search_term = 'Test'

        # check for the correct return value from mock_response
        self.assertEqual(find_character_appearances(search_term), test_search_data)



    def test_handle_search_results(self):
        """Tests handle search method, which returns a list of Character objects"""

        data = test_appearance_data

        # get the return value from the function
        search_res = handle_search_results(data)

        # check for the correct length of the returned list
        self.assertEqual(len(search_res), 4)

        # check for the correct data from the first result
        self.assertEqual(search_res[0].id, '2222')
        self.assertEqual(search_res[0].name, 'test_character')
        self.assertEqual(search_res[0].real_name, 'test_real_name')
        self.assertEqual(search_res[0].deck, 'test_deck')
        self.assertEqual(search_res[0].first_appear_issue_id, '3333')
        self.assertEqual(search_res[0].first_appear_issue_num, 4444)
        self.assertEqual(search_res[0].first_appear_issue_name, 'test_first_appear')
        self.assertEqual(search_res[0].total_appearances, 5555)
        self.assertEqual(search_res[0].icon_image_url, 'www.testiconurl.com')
        self.assertEqual(search_res[0].original_url, 'www.testoriginalurl.com')
        self.assertEqual(search_res[0].publisher_id, '6666')
        self.assertEqual(search_res[0].publisher_name, 'Test_Publisher')

        # check for the correct data from the last result
        self.assertEqual(search_res[3].id, '2222222')
        self.assertEqual(search_res[3].name, 'test_character3')
        self.assertEqual(search_res[3].real_name, None)
        self.assertEqual(search_res[3].deck, 'test_deck3')
        self.assertEqual(search_res[3].first_appear_issue_id, '3333333')
        self.assertEqual(search_res[3].first_appear_issue_num, 4444444)
        self.assertEqual(search_res[3].first_appear_issue_name, 'test_first_appear3')
        self.assertEqual(search_res[3].total_appearances, 5555555)
        self.assertEqual(search_res[3].icon_image_url, None)
        self.assertEqual(search_res[3].original_url, 'www.testoriginalurl3.com')
        self.assertEqual(search_res[3].publisher_id, None)
        self.assertEqual(search_res[3].publisher_name, None)