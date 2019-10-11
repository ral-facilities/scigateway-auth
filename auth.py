import requests


class ICATAuthenticator(object):
    def authenticate(self, mnemonic, credentials=None):
        if credentials is None:
            return requests.post("https://icat-dev.isis.stfc.ac.uk/icat/session",
                                 data={"json": f'{{"plugin": "{mnemonic}"}}'}).json()
        return requests.post("https://icat-dev.isis.stfc.ac.uk/icat/session",
                             data={"json": f'{{"plugin": {mnemonic},"credentials":{credentials}}}'})


class AuthenticationHandler(object):
    def __init__(self, mnemonic, credentials=None):
        self.mnemonic = mnemonic
        self.credentials = credentials if credentials is not None else None

    def _get_payload(self):
        authenticator = ICATAuthenticator()
        return authenticator.authenticate(self.mnemonic, credentials=self.credentials)

    def _pack_JWT(self, dictionary):
        # TODO
        return dictionary

    def get_jwt(self):
        return self._pack_JWT(self._get_payload())
