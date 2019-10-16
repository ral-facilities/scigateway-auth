from unittest import TestCase

from common.exceptions import BadMnemonicError
from src.auth import ICATAuthenticator


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

