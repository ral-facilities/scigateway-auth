from unittest import TestCase
import logging

from scigateway_auth.common.exceptions import MissingMnemonicError, AuthenticationError
from scigateway_auth.src.auth import requires_mnemonic


class TestRequires_mnemonic(TestCase):
    @classmethod
    def setUpClass(cls):
        logging.disable(logging.CRITICAL)

    @classmethod
    def tearDownClass(cls):
        logging.disable(logging.NOTSET)

    def test_missing_mnemonic(self):
        @requires_mnemonic
        def raise_missing_mnemonic_error():
            raise MissingMnemonicError()

        self.assertEqual(("Missing mnemonic", 400), raise_missing_mnemonic_error())

    def test_authentication_error(self):
        @requires_mnemonic
        def raise_authentication_error():
            raise AuthenticationError("Test")

        self.assertEqual(("Test", 403), raise_authentication_error())

    def test_general_exception(self):
        @requires_mnemonic
        def raise_exception():
            raise Exception

        self.assertEqual(("Something went wrong", 500), raise_exception())
