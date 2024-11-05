"""
Module for providing a class for handling authentication.
"""

import json
import logging
from typing import Any

import requests

from scigateway_auth.common.config import config
from scigateway_auth.common.exceptions import ICATAuthenticationError
from scigateway_auth.common.schemas import UserCredentialsPostRequestSchema

logger = logging.getLogger()


class ICATAuthenticator:
    """
    Class for managing authentication against an ICAT authenticator.
    """

    def authenticate(self, mnemonic: str, credentials: UserCredentialsPostRequestSchema = None) -> str:
        """
        Sends an authentication request to the ICAT authenticator and returns a session ID.

        :param mnemonic: The ICAT mnemonic to use to authenticate.
        :param credentials: The ICAT credentials to authenticate with.
        :raises ICATAuthenticationError: If there is a problem with the ICAT authenticator or the login details are
            invalid.
        :return: The ICAT session ID.
        """
        logger.info("Authenticating at %s with mnemonic: %s", config.icat_server.url, mnemonic)
        json_payload = (
            {"plugin": "anon"}
            if credentials is None
            else {
                "plugin": mnemonic,
                "credentials": [
                    {"username": credentials.username.get_secret_value()},
                    {"password": credentials.password.get_secret_value()},
                ],
            }
        )
        data = {"json": json.dumps(json_payload)}

        response = requests.post(
            f"{config.icat_server.url}/session",
            data=data,
            verify=config.icat_server.certificate_validation,
        )
        if response.status_code == 200:
            return response.json()["sessionId"]
        else:
            raise ICATAuthenticationError(response.json()["message"])

    def get_username(self, session_id: str) -> str:
        """
        Sends a request to ICAT to retrieve the user's username from a session ID.

        :param session_id: The session ID of the user who we want to get the username for.
        :raises ICATAuthenticationError: If there is a problem with the ICAT authenticator or the session ID is invalid.
        :return: The user's username.
        """
        logger.info("Retrieving username for session ID '%s' at %s", session_id, config.icat_server.url)
        response = requests.get(
            f"{config.icat_server.url}/session/{session_id}",
            verify=config.icat_server.certificate_validation,
        )
        if response.status_code == 200:
            return response.json()["userName"]
        else:
            raise ICATAuthenticationError(response.json()["message"])

    def get_authenticators(self) -> list[dict[str, Any]]:
        """
        Sends a request to ICAT to get the properties and parses the response to a list of authenticators.

        :return: The list of ICAT authenticator mnemonics and their friendly names.
        """
        logger.info("Querying ICAT at %s to get its list of mnemonics", config.icat_server.url)
        response = requests.get(
            f"{config.icat_server.url}/properties",
            verify=config.icat_server.certificate_validation,
        )
        properties = response.json()
        return properties["authenticators"]

    def refresh(self, session_id: str) -> None:
        """
        Sends a request to ICAT to refresh a session ID.

        :param session_id: The session ID to refresh.
        :raises ICATAuthenticationError: If there is a problem with the ICAT authenticator or the session ID cannot be
            refreshed.
        """
        logger.info("Refreshing session ID %s at %s", session_id, config.icat_server.url)
        response = requests.put(
            f"{config.icat_server.url}/session/{session_id}",
            verify=config.icat_server.certificate_validation,
        )
        if response.status_code != 204:
            raise ICATAuthenticationError("The session ID was unable to be refreshed")
