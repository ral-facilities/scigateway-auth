"""
Module for providing a class for handling JWTs.
"""

from datetime import datetime, timedelta, timezone
import logging
from typing import Any, Dict

from cryptography.hazmat.primitives import serialization
import jwt

from scigateway_auth.common.config import Config, get_config_value
from scigateway_auth.common.constants import (
    ACCESS_TOKEN_VALID_FOR,
    PRIVATE_KEY,
    PUBLIC_KEY,
    REFRESH_TOKEN_VALID_FOR,
)
from scigateway_auth.common.exceptions import BlacklistedJWTError, InvalidJWTError, JWTRefreshError
from scigateway_auth.common.schemas import UserCredentialsPostRequestSchema
from scigateway_auth.src.authentication import ICATAuthenticator

logger = logging.getLogger()


class JWTHandler:
    """
    Class for handling JWTs.
    """

    def get_access_token(self, mnemonic: str, credentials: UserCredentialsPostRequestSchema = None) -> str:
        """
        Generates a payload and returns a signed JWT access token.

        :param mnemonic: The ICAT mnemonic.
        :param credentials: The ICAT credentials.
        :return: The signed JWT access token.
        """
        logger.info("Getting an access token")
        authenticator = ICATAuthenticator()
        session_id = authenticator.authenticate(mnemonic, credentials)
        username = authenticator.get_username(session_id)
        is_user_admin = username in get_config_value(Config.ADMIN_USERS)

        payload = {
            "sessionId": session_id,
            "username": username,
            "userIsAdmin": is_user_admin,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_VALID_FOR),
        }
        return self._pack_jwt(payload)

    def get_refresh_token(self) -> str:
        """
        Generates a payload and returns a signed JWT refresh token.

        :return: The signed JWT refresh token.
        """
        logger.info("Getting a refresh token")
        return self._pack_jwt({"exp": datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_VALID_FOR)})

    def refresh_access_token(self, access_token: str, refresh_token: str):
        """
        Refreshes the JWT access token by updating its expiry time, provided that the JWT refresh token is valid.

        :param access_token: The JWT access token to refresh.
        :param refresh_token: The JWT refresh token.
        :raises JWTRefreshError: If the JWT access token cannot be refreshed.
        :return: JWT access token with an updated expiry time.
        """
        logger.info("Refreshing access token")

        if refresh_token in get_config_value(Config.BLACKLIST):
            raise BlacklistedJWTError(f"Attempted refresh from token in blacklist: {refresh_token}")

        self.verify_token(refresh_token)
        try:
            access_token_payload = self._get_jwt_payload(access_token, {"verify_exp": False})
            access_token_payload["exp"] = datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_VALID_FOR)
            authenticator = ICATAuthenticator()
            authenticator.refresh(access_token_payload["sessionId"])
            return self._pack_jwt(access_token_payload)
        except Exception as exc:
            message = "Unable to refresh access token"
            logger.exception(message)
            raise JWTRefreshError(message) from exc

    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verifies that the provided JWT token is valid. It does this by checking that it was signed by the corresponding
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

    def _create_jwt_payload(self, session_id: str, username: str, is_user_admin: bool) -> dict[str, Any]:
        """
        Creates a payload for the JWT tokens.

        :param session_id: The ICAT session ID.
        :param username: The ICAT username.
        :param is_user_admin: Whether the user is admin.
        :return: The payload for the JWT token.
        """
        return {
            "sessionId": session_id,
            "username": username,
            "userIsAdmin": is_user_admin,
        }

    def _get_jwt_payload(self, token: str, jwt_decode_options: dict | None = None) -> Dict[str, Any]:
        """
        Decodes the provided JWT token and gets its payload.

        :param token: The JWT token to decode and get payload from.
        :param jwt_decode_options: Any options to be passed to the `decode` method.
        :return: The payload from the provided JWT token.
        """
        logger.info("Decoding JWT token")
        return jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"], options=jwt_decode_options)

    def _pack_jwt(self, payload: dict) -> str:
        """
        Packs the provided payload into a JWT token and signs it.

        :param payload: The payload to be packed.
        :return: The encoded and signed JWT token.
        """
        logger.debug("Packing payload into a JWT token")
        bytes_key = bytes(PRIVATE_KEY, encoding="utf8")
        loaded_private_key = serialization.load_ssh_private_key(bytes_key, password=None)
        return jwt.encode(payload, loaded_private_key, algorithm="RS256")
