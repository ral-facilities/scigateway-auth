from unittest import TestCase, mock

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
        self.assertRaises(BadMnemonicError, self.authenticator._check_mnemonic, None)
        self.assertRaises(BadMnemonicError, self.authenticator._check_mnemonic, "test")
        self.assertRaises(BadMnemonicError, self.authenticator._check_mnemonic, 1)

