from unittest import TestCase, mock

import requests

from common.exceptions import AuthenticationError
from src.auth import ICATAuthenticator


class MockResponse(object):
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


def mock_good_icat_authenticate_request(*args, **kwargs):
    return MockResponse({"sessionId": "test"}, 200)

def mock_bad_icat_authenticate_request(*args, **kwargs):
    return MockResponse({"code": "SESSION", "message": "Error logging in. Please try again later"}, 400)

def mock_good_icat_properties_request(*args, **kwargs):
    return MockResponse({"authenticators": [{"mnemonic": "anon", "keys": []}]}, 200)

def mock_bad_icat_properties_request(*args, **kwargs):
    return MockResponse({}, 500)

class TestICATAuthenticator(TestCase):
    def setUp(self):
        self.authenticator = ICATAuthenticator()

    
    @mock.patch("requests.post", side_effect=mock_good_icat_authenticate_request)
    def test_authenticate_with_good_response(self, mock_post):
        result = self.authenticator.authenticate("test", {"username": "valid", "password": "credentials"})
        self.assertDictEqual(result, {"sessionId": "test"})

    @mock.patch("requests.post", side_effect=mock_bad_icat_authenticate_request)
    def test_authenticate_with_bad_response(self, mock_post):
        with self.assertRaises(AuthenticationError) as ctx:
            self.authenticator.authenticate("test", {"username": "valid", "password": "credentials"})
        self.assertEqual("Error logging in. Please try again later", str(ctx.exception))

    @mock.patch("requests.get", side_effect=mock_good_icat_properties_request)
    def test_get_authenticators_with_good_response(self, mock_get):
        result = self.authenticator.get_authenticators()
        self.assertEqual(result, [{"mnemonic": "anon", "keys": []}])

    @mock.patch("requests.get", side_effect=mock_bad_icat_properties_request)
    def test_get_authenticators_with_bad_response(self, mock_get):
        result = self.authenticator.get_authenticators()
        self.assertEqual(result, [])
