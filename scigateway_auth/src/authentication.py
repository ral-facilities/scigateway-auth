"""
Module for providing a class for interacting with ICAT.
"""

import json
import logging
from typing import Any

import requests

from scigateway_auth.common.config import config
from scigateway_auth.common.exceptions import ICATServerError, InvalidCredentialsError
from scigateway_auth.common.schemas import UserCredentialsPostRequestSchema

logger = logging.getLogger()


class ICATClient:
    """
    Class for managing interactions with an ICAT server.
    """

    @staticmethod
    def authenticate(mnemonic: str, credentials: UserCredentialsPostRequestSchema = None) -> str:
        """
        Sends an authentication request to the ICAT server and returns a session ID.

        :param mnemonic: The ICAT mnemonic to use to authenticate.
        :param credentials: The ICAT credentials to authenticate with.
        :raises InvalidCredentialsError: If the user credentials are invalid.
        :raises ICATError: If there is a problem with the ICAT server.
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
            timeout=config.icat_server.request_timeout_seconds,
        )
        if response.status_code == 200:
            return response.json()["sessionId"]
        elif response.status_code == 403:
            raise InvalidCredentialsError(response.json()["message"])
        else:
            raise ICATServerError(response.json()["message"])

    @staticmethod
    def get_username(session_id: str) -> str:
        """
        Sends a request to ICAT to retrieve the user's username from a session ID.

        :param session_id: The session ID of the user who we want to get the username for.
        :raises ICATError: If there is a problem with the ICAT server or the session ID is invalid.
        :return: The user's ICAT username.
        """
        logger.info("Retrieving username for session ID '%s' at %s", session_id, config.icat_server.url)
        response = requests.get(
            f"{config.icat_server.url}/session/{session_id}",
            verify=config.icat_server.certificate_validation,
            timeout=config.icat_server.request_timeout_seconds,
        )
        if response.status_code == 200:
            return response.json()["userName"]
        else:
            raise ICATServerError(response.json()["message"])

    @staticmethod
    def get_authenticators() -> list[dict[str, Any]]:
        """
        Sends a request to ICAT to get the properties and parses the response to a list of authenticators.

        :return: The list of ICAT authenticator mnemonics and their friendly names.
        """
        logger.info("Querying ICAT at %s to get its list of mnemonics", config.icat_server.url)
        response = requests.get(
            f"{config.icat_server.url}/properties",
            verify=config.icat_server.certificate_validation,
            timeout=config.icat_server.request_timeout_seconds,
        )
        properties = response.json()
        return properties["authenticators"]

    @staticmethod
    def refresh(session_id: str) -> None:
        """
        Sends a request to ICAT to refresh a session ID.

        :param session_id: The session ID to refresh.
        :raises ICATError: If there is a problem with the ICAT server or the session ID cannot be refreshed.
        """
        logger.info("Refreshing session ID %s at %s", session_id, config.icat_server.url)
        response = requests.put(
            f"{config.icat_server.url}/session/{session_id}",
            verify=config.icat_server.certificate_validation,
            timeout=config.icat_server.request_timeout_seconds,
        )
        if response.status_code != 204:
            raise ICATServerError("The session ID was unable to be refreshed")

    @staticmethod
    def get_user_instrument_ids(session_id: str, username: str) -> list[int]:
        """
        Get the IDs of the instruments where the user is an instrument scientist.

        :param session_id: The session ID of the user to use when querying ICAT.
        :param username: The user's ICAT username.
        """
        # The username here comes directly from ICAT rather than a user's input. The ICAT server also defends against
        # SQL injections.
        query = (
            "SELECT i.id FROM Instrument i JOIN i.instrumentScientists as isc JOIN isc.user u "  # noqa: S608
            f"WHERE u.name = {username!r}"
        )
        return ICATClient._fetch_ids_by_query(session_id, query)

    @staticmethod
    def _fetch_ids_by_query(session_id: str, query: str) -> list[int]:
        """
        Sends a request to ICAT to get the entity IDs specified in the provided query.

        :param session_id: The session ID of the user to use when querying ICAT.
        :raises ICATError: If there is a problem with the ICAT server or the session ID or query is invalid.
        """
        response = requests.get(
            f"{config.icat_server.url}/entityManager",
            params={"sessionId": session_id, "query": query},
            verify=config.icat_server.certificate_validation,
            timeout=config.icat_server.request_timeout_seconds,
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise ICATServerError(response.json()["message"])
