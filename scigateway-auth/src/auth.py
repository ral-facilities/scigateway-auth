import logging
from functools import wraps

import jwt
import requests

from common.constants import SECRET, ICAT_AUTH_URL
from common.exceptions import MissingMnemonicError

log = logging.getLogger()


class ICATAuthenticator(object):
    def authenticate(self, mnemonic, credentials=None):
        log.info(f"Authenticating at {ICAT_AUTH_URL} with mnemonic: {mnemonic}")
        if credentials is None:
            return requests.post(ICAT_AUTH_URL,
                                 data={"json": f'{{"plugin": "{mnemonic}"}}'}).json()

        return requests.post(ICAT_AUTH_URL,
                             data={"json": f'{{"plugin": {mnemonic},"credentials":{credentials}}}'})


class AuthenticationHandler(object):
    """
    An AuthenticationHandler can be used to verify JWTs, insert sessions into JWTs and create ICATAuthenticators to
    get ICAT session IDs
    """

    def __init__(self):
        self.mnemonic = None
        self.credentials = None

    def set_mnemonic(self, mnemonic):
        self.mnemonic = mnemonic

    def set_credentials(self, credentials):
        self.credentials = credentials

    def _get_payload(self):
        """
        Creates an ICATAuthenticator and calls the authenticate method to get a payload
        :return: The payload
        """
        log.info("Creating ICATAuthenticator")
        authenticator = ICATAuthenticator()
        return authenticator.authenticate(self.mnemonic, credentials=self.credentials)

    def _pack_jwt(self, dictionary):
        """
        Packs a given payload into a jwt
        :param dictionary: the payload to be packed
        :return: The encoded JWT
        """
        log.info("Encoding JWT")
        token = jwt.encode(dictionary, SECRET, algorithm="HS256")
        log.info("Returning JWT")
        return token.decode("utf-8")

    def get_jwt(self):
        """
        Return a signed JWT with ICAT session information inside
        :return: The JWT
        """
        return self._pack_jwt(self._get_payload())

    def verify_token(self, token):
        """
        Given a JWT, verify that it was signed by the API
        :param token: The JWT to be checked
        :return: - tuple with message and status code e.g. ("", 200)
        """
        try:
            log.info("Verifying token")
            jwt.decode(token, SECRET, algorithms=["HS256"])
            log.info("Token verified")
            return "", 200
        except:
            log.warn("Token could not be verified")
            return "Unauthorized", 403


def requires_mnemonic(method):
    """
    Decorator for the /login post method to handle the case where a mnemonic is not provided
    """

    @wraps(method)
    def wrapper(*args, **kwargs):
        try:
            return method(*args, **kwargs)
        except MissingMnemonicError as e:
            log.exception(e)
            return "Missing mnemonic", 400
        except Exception as e:
            log.exception(e)
            return "Something went wrong", 500

    return wrapper
