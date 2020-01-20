from unittest import TestCase, mock

import requests

from common.exceptions import BadMnemonicError, AuthenticationError
from src.auth import ICATAuthenticator


class MockResponse(object):
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data


def mock_authenticated_icat_new_session_request(*args, **kwargs):
    return MockResponse({"sessionId": "test"}, 200)


def mock_unauthenticated_icat_new_session_request(*args, **kwargs):
    return MockResponse({"code": "SESSION", "message": "Error logging in. Please try again later"}, 200)


def mock_successful_icat_refresh_session_request(*args, **kwargs):
    return MockResponse("", 204)


def mock_unsuccessful_icat_refresh_session_request(*args, **kwargs):
    return MockResponse({"code":"SESSION","message":"Unable to find user by sessionid: x"}, 403)


class TestICATAuthenticator(TestCase):
    def setUp(self):
        self.authenticator = ICATAuthenticator()

    def test__check_mnemonic(self):
        self.authenticator._check_mnemonic("ldap")
        self.authenticator._check_mnemonic("anon")
        self.authenticator._check_mnemonic("uows")
        self.authenticator._check_mnemonic("db")
        self.authenticator._check_mnemonic("simple")
        self.assertRaises(BadMnemonicError, self.authenticator._check_mnemonic, None)
        self.assertRaises(BadMnemonicError, self.authenticator._check_mnemonic, "test")
        self.assertRaises(BadMnemonicError, self.authenticator._check_mnemonic, 1)

    @mock.patch("requests.post", side_effect=mock_authenticated_icat_new_session_request)
    def test__is_authenticated_with_good_response(self, mock_get):
        result = self.authenticator._is_authenticated(requests.post(""))
        self.assertTrue(result)

    @mock.patch("requests.post", side_effect=mock_unauthenticated_icat_new_session_request)
    def test__ist_authenticated_with_bad_response(self, mock_get):
        result = self.authenticator._is_authenticated(requests.post(""))
        self.assertFalse(result)

    @mock.patch("requests.put", side_effect=mock_successful_icat_refresh_session_request)
    def test_refresh_success(self, mock_get):
        result = self.authenticator.refresh("valid session id")
        self.assertIsNone(result)

    @mock.patch("requests.put", side_effect=mock_unsuccessful_icat_refresh_session_request)
    def test_refresh_failure(self, mock_get):
        with self.assertRaises(AuthenticationError) as ctx:
            self.authenticator.refresh("invalid session id")
        self.assertEqual("The session ID was unable to be refreshed", str(ctx.exception))
