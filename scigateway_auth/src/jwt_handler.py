"""
Module for providing a class for handling JWTs.
"""

from datetime import datetime, timedelta, timezone
import logging
from typing import Any, Optional

from cryptography.hazmat.primitives import serialization
import jwt

from scigateway_auth.common.config import config
from scigateway_auth.common.constants import PRIVATE_KEY, PUBLIC_KEY
from scigateway_auth.common.exceptions import (
    BlacklistedJWTError,
    InvalidJWTError,
    JWTRefreshError,
    UsernameMismatchError,
)
from scigateway_auth.src.authentication import ICATClient

logger = logging.getLogger()


class JWTHandler:
    """
    Class for handling JWTs.
    """

    def get_access_token(
        self,
        icat_session_id: str,
        icat_username: str,
        icat_user_instrument_ids: list[int],
    ) -> str:
        """
        Generate a payload and return a signed JWT access token.

        :param icat_session_id: The ICAT session ID.
        :param icat_username: The user's ICAT username.
        :param icat_user_instrument_ids: The IDs of the instruments where the user is an instrument scientist.
        :return: The signed JWT access token.
        """
        logger.info("Getting an access token")
        payload = {
            "instruments": icat_user_instrument_ids,
            "sessionId": icat_session_id,
            "username": icat_username,
            "userIsAdmin": self._is_user_admin(icat_username),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=config.authentication.access_token_validity_minutes),
        }
        return self._pack_jwt(payload)

    def get_refresh_token(self, icat_username: str) -> str:
        """
        Generate a payload and return a signed JWT refresh token.

        :param icat_username: The user's ICAT username.
        :return: The signed JWT refresh token.
        """
        logger.info("Getting a refresh token")
        return self._pack_jwt(
            {
                "username": icat_username,
                "exp": datetime.now(timezone.utc) + timedelta(days=config.authentication.refresh_token_validity_days),
            },
        )

    def refresh_access_token(self, access_token: str, refresh_token: str):
        """
        Refresh the JWT access token by updating its expiry time, provided that the JWT refresh token is valid.

        :param access_token: The JWT access token to refresh.
        :param refresh_token: The JWT refresh token.
        :raises JWTRefreshError: If the JWT access token cannot be refreshed.
        :raises UsernameMismatchError: If the usernames in the access and refresh tokens do not match
        :return: JWT access token with an updated expiry time.
        """
        logger.info("Refreshing access token")

        if self._is_refresh_token_blacklisted(refresh_token):
            raise BlacklistedJWTError(f"Attempted refresh from token in blacklist: {refresh_token}")

        refresh_token_payload = self.verify_token(refresh_token)
        try:
            access_token_payload = self._get_jwt_payload(access_token, {"verify_exp": False})
            if access_token_payload["username"] != refresh_token_payload["username"]:
                raise UsernameMismatchError("The usernames in the access and refresh tokens do not match")

            access_token_payload["exp"] = datetime.now(timezone.utc) + timedelta(
                minutes=config.authentication.access_token_validity_minutes,
            )
            ICATClient.refresh(access_token_payload["sessionId"])
            return self._pack_jwt(access_token_payload)
        except Exception as exc:
            message = "Unable to refresh access token"
            logger.exception(message)
            raise JWTRefreshError(message) from exc

    def verify_token(self, token: str) -> dict[str, Any]:
        """
        Verify that the provided JWT token is valid. Do this by checking that it was signed by the corresponding
        private key and has not expired.

        :param token: The JWT token to be verified.
        :raises InvalidJWTError: If the JWT token is invalid.
        :return: The payload of the verified JWT token.
        """
        logger.info("Verifying JWT token is valid")
        try:
            return self._get_jwt_payload(token)
        except Exception as exc:
            message = "Invalid JWT token"
            logger.exception(message)
            raise InvalidJWTError(message) from exc

    @staticmethod
    def _get_jwt_payload(token: str, jwt_decode_options: Optional[dict] = None) -> dict[str, Any]:
        """
        Decode the provided JWT token and get its payload.

        :param token: The JWT token to decode and get payload from.
        :param jwt_decode_options: Any options to be passed to the `decode` method.
        :return: The payload from the provided JWT token.
        """
        logger.info("Decoding JWT token")
        return jwt.decode(
            token,
            PUBLIC_KEY,
            algorithms=[config.authentication.jwt_algorithm],
            options=jwt_decode_options,
        )

    @staticmethod
    def _is_refresh_token_blacklisted(refresh_token: str) -> bool:
        """
        Check if the provided refresh token is in the blacklist configuration to determine whether the token is valid
        for refreshing access tokens.

        :param refresh_token: The JWT refresh token to be checked.
        :return: `True` if the refresh token is blacklisted, `False` otherwise.
        """
        return refresh_token in config.authentication.jwt_refresh_token_blacklist

    @staticmethod
    def _is_user_admin(username: str) -> bool:
        """
        Check if the provided username is in the list of admin usernames configuration to determine if the user has
        admin privileges.

        :param username: The username to be checked.
        :return: `True` if the username is in the list of admin usernames, `False` otherwise.
        """
        return username in config.authentication.admin_users

    @staticmethod
    def _pack_jwt(payload: dict) -> str:
        """
        Pack the provided payload into a JWT token and sign it.

        :param payload: The payload to be packed.
        :return: The encoded and signed JWT token.
        """
        logger.debug("Packing payload into a JWT token")
        bytes_key = bytes(PRIVATE_KEY, encoding="utf8")
        loaded_private_key = serialization.load_ssh_private_key(bytes_key, password=None)
        return jwt.encode(payload, loaded_private_key, algorithm=config.authentication.jwt_algorithm)
