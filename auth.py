from abc import ABC, abstractmethod

import requests


class ICATAuthenticator(ABC):
    @abstractmethod
    def authenticate(self, credentials):
        pass


class SimpleICATAuthenticator(ICATAuthenticator):
    def authenticate(self, credentials):
        pass


class LDAPICATAuthenticator(ICATAuthenticator):
    def authenticate(self, credentials):
        pass


class UOWSICATAuthenticator(ICATAuthenticator):
    def authenticate(self, credentials):
        pass


class AnonICATAuthenticator(ICATAuthenticator):

def get_authenticator(mnemonic):
    if mnemonic == "simple":
        return SimpleICATAuthenticator()
    if mnemonic == "uows":
        return UOWSICATAuthenticator()
    if mnemonic == "anon":
        return AnonICATAuthenticator()
    if mnemonic == "ldap":
        return LDAPICATAuthenticator()


