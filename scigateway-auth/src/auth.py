import logging
import json

from functools import wraps

import jwt
import requests

from common.constants import PRIVATE_KEY, PUBLIC_KEY, ICAT_URL, BLACKLIST, ACCESS_TOKEN_VALID_FOR, REFRESH_TOKEN_VALID_FOR, VERIFY
from common.exceptions import MissingMnemonicError, AuthenticationError

import datetime


def current_time():
    return datetime.datetime.now()


log = logging.getLogger()


class ICATAuthenticator(object):
    def authenticate(self, mnemonic, credentials=None):
        """
        Sends an authentication request to the icat authenticator and returns the session_id
        :param mnemonic: The mnemonic to use to authenticate
        :param credentials: The credentials to authenticate with
        :return: The session id
        """
        log.info(
            f"Authenticating at {ICAT_URL} with mnemonic: {mnemonic}")
        data = {"json": json.dumps({"plugin": "anon"})} if credentials is None else {
            "json": json.dumps({"plugin": mnemonic, "credentials": credentials})}
        response = requests.post(
            f"{ICAT_URL}/session", data=data, verify=VERIFY)
        if response.status_code is 200:
            return response.json()["sessionId"]
        else:
            raise AuthenticationError(response.json()["message"])

    def get_username(self, session_id):
        """
        Sends requests to ICAT to retrieve the user's username
        :param session_id: The session id of the user who we want to get info for
        :return: The user's username
        """
        log.info(
            f"Retrieving username for session id {session_id} at {ICAT_URL}")
        response = requests.get(f"{ICAT_URL}/session/{session_id}", verify=VERIFY)
        if response.status_code is 200:
            return response.json()["userName"]
        else:
            raise AuthenticationError(response.json()["message"])

    def get_authenticators(self):
        """
        Sends an request to ICAT to get the properties and parses the response to a list of authenticators
        :return: The list of ICAT authenticator mnemonics and their friendly names
        """
        log.info(
            f"Querying ICAT at {ICAT_URL} to get its list of mnemonics")
        response = requests.get(f"{ICAT_URL}/properties", verify=VERIFY)
        properties = response.json()
        return properties["authenticators"]

    def refresh(self, session_id):
        """
        Sends an refresh session_id request to ICAT
        :param session_id: The session ID to refresh
        """
        log.info(
            f"Refreshing session ID {session_id} at {ICAT_URL}")
        response = requests.put(
            f"{ICAT_URL}/session/{session_id}", verify=VERIFY)
        if response.status_code != 204:
            raise AuthenticationError(
                "The session ID was unable to be refreshed")


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

    def get_authenticators(self):
        authenticator = ICATAuthenticator()
        return authenticator.get_authenticators()

    def _get_payload(self):
        """
        Creates an ICATAuthenticator and calls the authenticate method to get a payload
        :return: The payload
        """
        log.info("Creating ICATAuthenticator")
        authenticator = ICATAuthenticator()
        session_id = authenticator.authenticate(
            self.mnemonic, credentials=self.credentials)
        username = authenticator.get_username(session_id)
        return {
            "sessionId": session_id,
            "username": username
        }

    def _pack_jwt(self, dictionary):
        """
        Packs a given payload into a jwt
        :param dictionary: the payload to be packed
        :return: The encoded JWT
        """
        log.info("Encoding JWT")
        token = jwt.encode(dictionary, PRIVATE_KEY, algorithm="RS256")
        log.info("Returning JWT")
        return token.decode("utf-8")

    def get_access_token(self):
        """
        Return a signed JWT with ICAT session information inside
        :return: The access JWT
        """
        payload = self._get_payload()
        payload['exp'] = current_time(
        ) + datetime.timedelta(minutes=ACCESS_TOKEN_VALID_FOR)
        return self._pack_jwt(payload)

    def get_refresh_token(self):
        """
        Return a signed JWT with to be used as a refresh token
        :return: The refresh JWT
        """
        return self._pack_jwt({'exp': current_time() + datetime.timedelta(minutes=REFRESH_TOKEN_VALID_FOR)})

    def verify_token(self, token):
        """
        Given a JWT, verify that it was signed by the API
        :param token: The JWT to be checked
        :return: - tuple with message and status code e.g. ("", 200)
        """
        try:
            log.info("Verifying token")
            jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
            log.info("Token verified")
            return "", 200
        except:
            log.warning("Token could not be verified")
            return "Unauthorized", 403

    def refresh_token(self, refresh_token, prev_access_token):
        """
        Given a refresh token, generate a new access token if the refresh token is valid
        and the previous access token allows for a refresh
        :param refresh_token: The refresh token to be checked
        :param prev_access_token: The access token to be refreshed
        :return: - tuple with message and status code e.g. ("", 200)
        """
        try:
            log.info("Refreshing token")
            jwt.decode(refresh_token, PUBLIC_KEY, algorithms=["RS256"])
            if refresh_token in BLACKLIST:
                log.warning(
                    f"Attempted refresh from token in blacklist: {token}")
                raise Exception("JWT in blacklist")
            log.info("Token verified")
        except:
            log.warning("Refresh token was not valid")
            return "Refresh token was not valid", 403

        try:
            payload = jwt.decode(prev_access_token, PUBLIC_KEY, algorithms=[
                "RS256"], options={'verify_exp': False})
            payload['exp'] = (current_time()
                              + datetime.timedelta(minutes=ACCESS_TOKEN_VALID_FOR))

            log.info("Creating ICATAuthenticator")
            authenticator = ICATAuthenticator()
            authenticator.refresh(payload["sessionId"])
            return self._pack_jwt(payload), 200
        except:
            log.warning("Unable to refresh token")
            return "Unable to refresh token", 403


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
        except AuthenticationError as e:
            log.exception(e)
            return str(e), 403
        except Exception as e:
            log.exception(e)
            return "Something went wrong", 500

    return wrapper
