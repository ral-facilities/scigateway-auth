from unittest import TestCase, mock

import requests

from common.exceptions import BadMnemonicError
from src.auth import ICATAuthenticator


def mock_authenticated_icat_requests(*args, **kwargs):
    class MockResponse(object):
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    return MockResponse({"sessionId": "test"}, 200)


def mock_unauthenticated_icat_request(*args, **kwargs):
    class MockResponse(object):
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    return MockResponse({"code": "SESSION", "message": "Error logging in. Please try again later"}, 200)


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

    @mock.patch("requests.post", side_effect=mock_authenticated_icat_requests)
    def test__is_authenticated_with_good_response(self, mock_get):
        result = self.authenticator._is_authenticated(requests.post(""))
        self.assertTrue(result)

    @mock.patch("requests.post", side_effect=mock_unauthenticated_icat_request)
    def test__ist_authenticated_with_bad_response(self, mock_get):
        result = self.authenticator._is_authenticated(requests.post(""))
        self.assertFalse(result)
