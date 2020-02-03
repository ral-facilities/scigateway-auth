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


def mock_successful_icat_new_session_request(*args, **kwargs):
    return MockResponse({"sessionId": "test"}, 200)


def mock_unsuccessful_icat_new_session_request(*args, **kwargs):
    return MockResponse({"code": "SESSION", "message": "Error logging in. Please try again later"}, 400)

def mock_successful_icat_session_get_request(*args, **kwargs):
    return MockResponse({"userName": "test name", "remainingMinutes": 60}, 200)

def mock_unsuccessful_icat_session_get_request(*args, **kwargs):
    return MockResponse({"code": "SESSION", "message": "Unable to find user by sessionid: test"}, 400)

def mock_successful_icat_refresh_session_request(*args, **kwargs):
    return MockResponse("", 204)


def mock_unsuccessful_icat_refresh_session_request(*args, **kwargs):
    return MockResponse({"code": "SESSION", "message": "Unable to find user by sessionid: x"}, 403)


def mock_successful_icat_properties_request(*args, **kwargs):
    return MockResponse({"authenticators": [{"mnemonic": "anon", "keys": []}]}, 200)


def mock_unsuccessful_icat_properties_request(*args, **kwargs):
    return MockResponse({}, 500)


class TestICATAuthenticator(TestCase):
    def setUp(self):
        self.authenticator = ICATAuthenticator()

    @mock.patch("requests.put", side_effect=mock_successful_icat_refresh_session_request)
    def test_refresh_success(self, mock_get):
        result = self.authenticator.refresh("valid session id")
        self.assertIsNone(result)

    @mock.patch("requests.put", side_effect=mock_unsuccessful_icat_refresh_session_request)
    def test_refresh_failure(self, mock_get):
        with self.assertRaises(AuthenticationError) as ctx:
            self.authenticator.refresh("invalid session id")
        self.assertEqual(
            "The session ID was unable to be refreshed", str(ctx.exception))

    @mock.patch("requests.post", side_effect=mock_successful_icat_new_session_request)
    def test_authenticate_with_good_response(self, mock_post):
        result = self.authenticator.authenticate("test", {"username": "valid", "password": "credentials"})
        self.assertEqual(result, "test")

    @mock.patch("requests.post", side_effect=mock_unsuccessful_icat_new_session_request)
    def test_authenticate_with_bad_response(self, mock_post):
        with self.assertRaises(AuthenticationError) as ctx:
            self.authenticator.authenticate(
                "test", {"username": "valid", "password": "credentials"})
        self.assertEqual(
            "Error logging in. Please try again later", str(ctx.exception))

    @mock.patch("requests.get", side_effect=mock_successful_icat_session_get_request)
    def test_get_username_with_good_response(self, mock_post):
        result = self.authenticator.get_username("test")
        self.assertEqual(result, "test name")

    @mock.patch("requests.get", side_effect=mock_unsuccessful_icat_session_get_request)
    def test_get_username_with_bad_response(self, mock_post):
        with self.assertRaises(AuthenticationError) as ctx:
            self.authenticator.get_username("test")
        self.assertEqual("Unable to find user by sessionid: test", str(ctx.exception))

    @mock.patch("requests.get", side_effect=mock_successful_icat_properties_request)
    def test_get_authenticators_with_good_response(self, mock_get):
        result = self.authenticator.get_authenticators()
        self.assertEqual(result, [{"mnemonic": "anon", "keys": []}])

    @mock.patch("requests.get", side_effect=mock_unsuccessful_icat_properties_request)
    def test_get_authenticators_with_bad_response(self, mock_get):
        with self.assertRaises(KeyError) as ctx:
            self.authenticator.get_authenticators()
        self.assertEqual("'authenticators'", str(ctx.exception))
