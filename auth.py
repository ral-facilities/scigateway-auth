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
    def authenticate(self, credentials):
        return requests.post("https://icat-dev.isis.stfc.ac.uk/icat/session",
                             data={"json": "{\"plugin\": \"anon\"}"}).json()

def get_authenticator(mnemonic):
    if mnemonic == "simple":
        return SimpleICATAuthenticator()
    if mnemonic == "uows":
        return UOWSICATAuthenticator()
    if mnemonic == "anon":
        return AnonICATAuthenticator()
    if mnemonic == "ldap":
        return LDAPICATAuthenticator()


class AuthenticationHandler(object):
    def __init__(self, mnemonic, credentials=None):
        self.mnemonic = mnemonic
        self.credentials = credentials if credentials is not None else None

    def _get_payload(self):
        authenticator = get_authenticator(self.mnemonic)
        return authenticator.authenticate(self.credentials)

    def _pack_JWT(self, dictionary):
        # TODO
        return dictionary

    def get_jwt(self):
        return self._pack_JWT(self._get_payload())

