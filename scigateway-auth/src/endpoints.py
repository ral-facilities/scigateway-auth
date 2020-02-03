import logging

from flask import request
from flask_restful import Resource

from common.exceptions import MissingMnemonicError
from src.auth import AuthenticationHandler, requires_mnemonic

log = logging.getLogger()


class Endpoint(Resource):
    """
    Subclass of the flask restful resource class. This gives endpoints their own AuthenticationHandlers
    """

    def __init__(self):
        super().__init__()
        self.auth_handler = AuthenticationHandler()


class AuthenticatorsEndpoint(Endpoint):
    def get(self):
        """
        The get method for the /authenticators endpoint.  Returns a list of valid ICAT authenticators
        :return: The list of ICAT authenticators
        """
        try:
            return self.auth_handler.get_authenticators(), 200
        except KeyError:
            return "Failed to retrieve authenticators", 500


class LoginEndpoint(Endpoint):
    """
    Subclass of Endpoint to give the /login endpoint a method to extract the mnemonic and credentials from the json in
    the post body.
    """

    def get_credentials_from_post_body(self):
        """
        Gets the mnemonic and the credentials from the post body and set them for AuthenticationHandler
        """
        data = request.json
        try:
            log.info("Getting mnemonic from post body")
            self.auth_handler.set_mnemonic(data["mnemonic"])
        except KeyError:
            raise MissingMnemonicError("No mnemonic")
        try:
            log.info("Attempting to get credentials from post body")
            credentials = [{key: value}
                           for key, value in data["credentials"].items()]

            self.auth_handler.set_credentials(credentials)
        except KeyError:
            log.info("No credentials given")
            pass

    @requires_mnemonic
    def post(self):
        """
        The post method for the /login endpoint. Uses the ICATAuthenticator to obtain a session_id and returns a JWT
        with the session_id as the payload
        :return: The JWT
        """
        self.get_credentials_from_post_body()
        return self.auth_handler.get_access_token(), 200, {'Set-Cookie': f'scigateway:refresh_token={self.auth_handler.get_refresh_token()}; Max-Age=604800; Secure; HttpOnly; SameSite=Lax'}


class VerifyEndpoint(Endpoint):
    def post(self):
        """
        Checks if the posted JWT was signed by the api
        :return: ("", 200) if it is a valid JWT, ("Unauthorized",403) otherwise.
        """
        return self.auth_handler.verify_token(request.json["token"])


class RefreshEndpoint(Endpoint):
    def post(self):
        """
        Gives a new access token given a refresh token cookie and an expired access token
        :return: ("", 200) if it is a valid refresh token,
                 ("Unauthorized",403) if it's invalid or
                 ("No refresh token cookie found",400) if no refresh token is found.
                 ("No previous access token found",400) if no access token is found.
        """
        try:
            refresh_token = request.cookies["scigateway:refresh_token"]
        except KeyError:
            log.info("No refresh token cookie found")
            return "No refresh token cookie found", 400
        try:
            access_token = request.json["token"]
        except (TypeError, KeyError):
            log.info("No access token found")
            return "No access token found", 400
        return self.auth_handler.refresh_token(refresh_token, access_token)
        
        
