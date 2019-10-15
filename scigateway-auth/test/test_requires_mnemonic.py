from unittest import TestCase

from common.exceptions import MissingMnemonicError
from src.auth import requires_mnemonic


class TestRequires_mnemonic(TestCase):
    def test_missing_mnemonic(self):
        @requires_mnemonic
        def raise_missing_mnemonic_error():
            raise MissingMnemonicError()

        self.assertEqual(("Missing mnemonic", 400), raise_missing_mnemonic_error())

    def test_general_exception(self):
        @requires_mnemonic
        def raise_exception():
            raise Exception

        self.assertEqual(("Something went wrong", 500), raise_exception())
