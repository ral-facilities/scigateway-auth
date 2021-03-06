import logging

from flask import request
from flask_restful import Resource
import jsonschema
from jsonschema.exceptions import ValidationError

from scigateway_auth.common.constants import SECURE
from scigateway_auth.common.exceptions import MissingMnemonicError
from scigateway_auth.src.admin import MaintenanceMode, ScheduledMaintenanceMode
from scigateway_auth.src.auth import AuthenticationHandler, requires_mnemonic

log = logging.getLogger()


class Endpoint(Resource):
    """
    Subclass of the flask restful resource class. This gives endpoints their own
    AuthenticationHandlers
    """

    def __init__(self):
        super().__init__()
        self.auth_handler = AuthenticationHandler()
        self.maintenance_mode = MaintenanceMode()
        self.scheduled_maintenance_mode = ScheduledMaintenanceMode()


class AuthenticatorsEndpoint(Endpoint):
    def get(self):
        """
        The get method for the /authenticators endpoint.  Returns a list of valid ICAT
        authenticators
        :return: The list of ICAT authenticators
        """
        try:
            return self.auth_handler.get_authenticators(), 200
        except KeyError:
            return "Failed to retrieve authenticators", 500


class LoginEndpoint(Endpoint):
    """
    Subclass of Endpoint to give the /login endpoint a method to extract the
    mnemonic and credentials from the json in the post body.
    """

    def get_credentials_from_post_body(self):
        """
        Gets the mnemonic and the credentials from the post body and set them for
        AuthenticationHandler
        """
        data = request.json
        try:
            log.info("Getting mnemonic from post body")
            self.auth_handler.set_mnemonic(data["mnemonic"])
        except KeyError:
            raise MissingMnemonicError("No mnemonic")
        try:
            log.info("Attempting to get credentials from post body")
            credentials = [{key: value} for key, value in data["credentials"].items()]

            self.auth_handler.set_credentials(credentials)
        except KeyError:
            log.info("No credentials given")
            pass

    @requires_mnemonic
    def post(self):
        """
        The post method for the /login endpoint. Uses the ICATAuthenticator to obtain a
        session_id and returns a JWT with the session_id as the payload
        :return: The JWT
        """
        self.get_credentials_from_post_body()
        return (
            self.auth_handler.get_access_token(),
            200,
            {
                "Set-Cookie": "scigateway:refresh_token="
                f"{self.auth_handler.get_refresh_token()}; Max-Age=604800; "
                f'{"Secure;" if SECURE else ""}HttpOnly; SameSite=Lax',
            },
        )


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
        Gives a new access token given a refresh token cookie and an expired
        access token
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


class MaintenanceEndpoint(Endpoint):
    """
    Subclass of Endpoint to give the /maintenance endpoint a method to extract
    the token and maintenance from the JSON in the PUT body.
    """

    def get(self):
        """
        The GET method for the /maintenance endpoint. Returns a JSON object
        that represents the maintenance mode state.
        :return: The maintenance mode state in form of a JSON object.
        """
        try:
            return self.maintenance_mode.get_state(), 200
        except IOError:
            return "Failed to retrieve maintenance mode state", 500

    def put(self):
        """
        The PUT method for the /maintenance endpoint. Updates the maintenance
        mode state given an access token and a state.
        :return: ("Maintenance mode state successfully updated", 200) if state
                 update is successful,
                 ("[Any JSON validation error message], 400") if the JSON data
                 is invalid,
                 ("Access token was not valid", 403) if the access token is
                 invalid,
                 ("Unauthorized", 403) if the user is not admin or
                 ("Failed to update maintenance mode state", 500) if an error
                 occurs while the JSON file is updated.
        """
        put_schema = {
            "type": "object",
            "properties": {
                "token": {"type": "string"},
                "maintenance": {
                    "type": "object",
                    "properties": {
                        "show": {"type": "boolean"},
                        "message": {"type": "string"},
                    },
                    "required": ["show", "message"],
                },
            },
            "required": ["token", "maintenance"],
        }
        data = request.json
        try:
            jsonschema.validate(instance=data, schema=put_schema)
        except ValidationError as error:
            log.info(error.args)
            return str(error), 400

        return self.maintenance_mode.set_state(data["token"], data["maintenance"])


class ScheduledMaintenanceEndpoint(Endpoint):
    """
    Subclass of Endpoint to give the /scheduled_maintenance endpoint a method
    to extract the token and scheduledMaintenance from the JSON in the PUT
    body.
    """

    def get(self):
        """
        The GET method for the /scheduled_maintenance endpoint. Returns a JSON
        object that represents the scheduled maintenance mode state.
        :return: The scheduled maintenance mode state in form of a JSON object.
        """
        try:
            return self.scheduled_maintenance_mode.get_state(), 200
        except IOError:
            return "Failed to return scheduled maintenance state", 500

    def put(self):
        """
        The PUT method for the /scheduled_maintenance endpoint. Updates the
        scheduled maintenance mode state given an access token and a state.
        :return: ("Scheduled maintenance mode state successfully updated", 200)
                 if state update is successful,
                 ("[Any JSON validation error message], 400") if the JSON data
                 is invalid,
                 ("Access token was not valid", 403) if the access token is
                 invalid,
                 ("Unauthorized", 403) if the user is not admin or
                 ("Failed to update scheduled maintenance mode state", 500) if
                 an error occurs while the JSON file is updated.
        """
        put_schema = {
            "type": "object",
            "properties": {
                "token": {"type": "string"},
                "scheduledMaintenance": {
                    "type": "object",
                    "properties": {
                        "show": {"type": "boolean"},
                        "message": {"type": "string"},
                    },
                    "required": ["show", "message"],
                },
            },
            "required": ["token", "scheduledMaintenance"],
        }
        data = request.json
        try:
            jsonschema.validate(instance=data, schema=put_schema)
        except ValidationError as error:
            log.info(error.args)
            return str(error), 400

        return self.scheduled_maintenance_mode.set_state(
            data["token"],
            data["scheduledMaintenance"],
        )
