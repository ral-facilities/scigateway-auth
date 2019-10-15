import jwt
import requests

from common.constants import SECRET


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

    def _pack_jwt(self, dictionary):
        token = jwt.encode(dictionary, SECRET, algorithm="HS256")
        return token.decode("utf-8")

    def get_jwt(self):
        return self._pack_jwt(self._get_payload())

def verify_token(token):
    try:
        jwt.decode(token, SECRET, algorithms=["HS256"])
        return "", 200
    except:
        return "Unauthorized", 403