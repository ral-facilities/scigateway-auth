from flask import request
from flask_restful import Resource

from common.exceptions import MissingMnemonicError
from src.auth import AuthenticationHandler, requires_mnemonic


class Endpoint(Resource):
    """
    Subclass of the flask restful resource class. This gives both endpoints their own AuthenticationHandlers
    """
    def __init__(self):
        super().__init__()
        self.auth_handler = AuthenticationHandler()


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
            self.auth_handler.set_mnemonic(data["mnemonic"])
        except KeyError:
            raise MissingMnemonicError("No mnemonic")
        try:
            self.auth_handler.set_credentials(data["credentials"])
        except KeyError:
            pass

    @requires_mnemonic
    def post(self):
        """
        The post method for the /login endpoint. Uses the ICATAuthenticator to obtain a session_id and returns a JWT
        with the session_id as the payload
        :return: The JWT
        """
        self.get_credentials_from_post_body()
        return self.auth_handler.get_jwt(), 200


class VerifyEndpoint(Endpoint):
    def post(self):
        """
        Checks if the posted JWT was signed by the api
        :return: ("", 200) if it is a valid JWT, ("Unauthorized",403) otherwise.
        """
        return self.auth_handler.verify_token(request.json["token"])
