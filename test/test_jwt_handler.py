"""
Unit tests for the `JWTHandler` class.
"""

from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest

from scigateway_auth.common.exceptions import (
    BlacklistedJWTError,
    ICATAuthenticationError,
    InvalidJWTError,
    JWTRefreshError,
)
from scigateway_auth.src.jwt_handler import JWTHandler
from test.mock_data import (
    EXPECTED_ACCESS_TOKEN_ADMIN,
    EXPECTED_ACCESS_TOKEN_NON_ADMIN,
    EXPECTED_REFRESH_TOKEN,
    EXPIRED_ACCESS_TOKEN_NON_ADMIN,
    EXPIRED_REFRESH_TOKEN,
    VALID_ACCESS_TOKEN_NON_ADMIN,
    VALID_REFRESH_TOKEN,
)


class TestJWTHandler:
    """
    Unit tests for the `JWTHandler` class.
    """

    icat_username = "test-username"
    icat_session_id = "test-session-id"
    mock_icat_authenticator: Mock
    jwt_handler = JWTHandler()

    def mock_datetime_now(self) -> datetime:
        """
        Mock function to return a predefined datetime object.

        :return: Predefined datetime object.
        """
        return datetime(2024, 1, 17, 10, 0, 0, 0, tzinfo=timezone.utc)

    @patch("scigateway_auth.src.jwt_handler.datetime")
    def test_get_access_token_non_admin(self, mock_datetime):
        """
        Test that `get_access_token` method successfully returns a JWT access token when user is not an admin.
        """
        mock_datetime.now.return_value = self.mock_datetime_now()

        access_token = self.jwt_handler.get_access_token(self.icat_session_id, self.icat_username)

        assert access_token == EXPECTED_ACCESS_TOKEN_NON_ADMIN

    @patch("scigateway_auth.src.jwt_handler.config.authentication.admin_users", new=[icat_username])
    @patch("scigateway_auth.src.jwt_handler.datetime")
    def test_get_access_token_admin(self, mock_datetime):
        """
        Test that `get_access_token` method successfully returns a JWT access token when user is an admin.
        """
        mock_datetime.now.return_value = self.mock_datetime_now()

        access_token = self.jwt_handler.get_access_token(self.icat_session_id, self.icat_username)

        assert access_token == EXPECTED_ACCESS_TOKEN_ADMIN

    @patch("scigateway_auth.src.jwt_handler.datetime")
    def test_get_refresh_token(self, mock_datetime):
        """
        Test that `get_refresh_token` method successfully returns a JWT refresh token.
        """
        mock_datetime.now.return_value = self.mock_datetime_now()

        refresh_token = self.jwt_handler.get_refresh_token(self.icat_username)

        assert refresh_token == EXPECTED_REFRESH_TOKEN

    @patch("scigateway_auth.src.jwt_handler.ICATAuthenticator.refresh", return_value=None)
    @patch("scigateway_auth.src.jwt_handler.datetime")
    def test_refresh_access_token(self, mock_datetime, mock_icat_authenticator_refresh):
        """
        Test that `refresh_access_token` method successfully returns a new JWT access token when provided a valid
        refresh token.
        """
        mock_datetime.now.return_value = self.mock_datetime_now()

        access_token = self.jwt_handler.refresh_access_token(EXPIRED_ACCESS_TOKEN_NON_ADMIN, VALID_REFRESH_TOKEN)

        assert access_token == EXPECTED_ACCESS_TOKEN_NON_ADMIN

    @patch(
        "scigateway_auth.src.jwt_handler.config.authentication.jwt_refresh_token_blacklist",
        new=[VALID_REFRESH_TOKEN],
    )
    def test_refresh_access_token_with_blacklisted_refresh_token(self):
        """
        Test that `refresh_access_token` raises `BlacklistedJWTError` when attempting to refresh with a blacklisted
        refresh token.
        """
        with pytest.raises(BlacklistedJWTError) as exc:
            self.jwt_handler.refresh_access_token(EXPIRED_ACCESS_TOKEN_NON_ADMIN, VALID_REFRESH_TOKEN)
        assert str(exc.value) == f"Attempted refresh from token in blacklist: {VALID_REFRESH_TOKEN}"

    def test_refresh_access_token_with_expired_refresh_token(self):
        """
        Test that `refresh_access_token` raises `InvalidJWTError` when attempting to refresh with an expired refresh
        token.
        """
        with pytest.raises(InvalidJWTError) as exc:
            self.jwt_handler.refresh_access_token(EXPIRED_ACCESS_TOKEN_NON_ADMIN, EXPIRED_REFRESH_TOKEN)
        assert str(exc.value) == "Invalid JWT token"

    def test_refresh_access_token_with_invalid_access_token(self):
        """
        Test that `refresh_access_token` raises `JWTRefreshError` when attempting to refresh with an invalid access
        token.
        """
        with pytest.raises(JWTRefreshError) as exc:
            self.jwt_handler.refresh_access_token(EXPIRED_ACCESS_TOKEN_NON_ADMIN + "1", VALID_REFRESH_TOKEN)
        assert str(exc.value) == "Unable to refresh access token"

    def test_refresh_access_token_with_with_non_matching_usernames(self):
        """
        Test that `refresh_access_token` raises `JWTRefreshError` when access token and refresh token have non-matching
        usernames.
        """
        access_token = (
            "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzZXNzaW9uSWQiOiJ0ZXN0LXNlc3Npb24taWQiLCJ1c2VybmFtZSI6InVzZXIxMjMiL"  # noqa: S105
            "CJ1c2VySXNBZG1pbiI6ZmFsc2UsImV4cCI6MTcwNTQ4NzQwMH0.J0ygnF1volh5cWl2xRLt1jahh1IAzYBDdXY5KN0IGpA_egAPXMiFjkF"
            "EJYrFacz-1AA_NTU2cdHiKNpmPwqj_WxGDfe9eU6snhJSjQgLfPrs-Yd9DQpWEjYeA73gj6MW72qy44uBVd4BeqHYWGWbgRLwgb-l7WrYJ"
            "zAd_AzTpn3-WCIgNXGp08o4fJ9d36YZQVRnAzKgYeBIMX13lFRXE0A1Roscjj94xG0EqTqLGwqngs2kbdFPT0vVmUMJeXeSEiIhZoDx3eB"
            "jTcZnMEOqUODI9y8OKWq5csIT4L5HYrv0_5SR78BM4uv8-9E_Lqvsw64wN35fZ8EI-_gWwJ0qqA"
        )

        with pytest.raises(JWTRefreshError) as exc:
            self.jwt_handler.refresh_access_token(access_token, VALID_REFRESH_TOKEN)
        assert str(exc.value) == "Unable to refresh access token"

    @patch("scigateway_auth.src.jwt_handler.ICATAuthenticator.refresh", side_effect=ICATAuthenticationError)
    def test_refresh_access_token_icat_authenticator_refresh_failure(self, mock_icat_authenticator_refresh):
        """
        Test that `refresh_access_token` raises `JWTRefreshError` when `ICATAuthenticator.refresh` fails.
        """
        with pytest.raises(JWTRefreshError) as exc:
            self.jwt_handler.refresh_access_token(EXPIRED_ACCESS_TOKEN_NON_ADMIN, VALID_REFRESH_TOKEN)
        assert str(exc.value) == "Unable to refresh access token"

    def test_verify_token_with_access_token(self):
        """
        Test that `verify_token` method successfully verifies a valid JWT access token.
        """
        payload = self.jwt_handler.verify_token(VALID_ACCESS_TOKEN_NON_ADMIN)

        assert payload == {
            "sessionId": self.icat_session_id,
            "username": self.icat_username,
            "userIsAdmin": False,
            "exp": 253402300799,
        }

    def test_verify_token_with_refresh_token(self):
        """
        Test that `verify_token` method successfully verifies a valid JWT refresh token.
        """
        payload = self.jwt_handler.verify_token(VALID_REFRESH_TOKEN)

        assert payload == {"username": self.icat_username, "exp": 253402300799}

    def test_verify_token_with_expired_access_token(self):
        """
        Test that `verify_token` raises `InvalidJWTError` when verifying an expired access token.
        """
        with pytest.raises(InvalidJWTError) as exc:
            self.jwt_handler.verify_token(EXPIRED_ACCESS_TOKEN_NON_ADMIN)
        assert str(exc.value) == "Invalid JWT token"

    def test_verify_token_with_expired_refresh_token(self):
        """
        Test that `verify_token` raises `InvalidJWTError` when verifying an expired refresh token.
        """
        with pytest.raises(InvalidJWTError) as exc:
            self.jwt_handler.verify_token(EXPIRED_REFRESH_TOKEN)
        assert str(exc.value) == "Invalid JWT token"

    def test_verify_token_with_invalid_token(self):
        """
        Test that `verify_token` raises `InvalidJWTError` when verifying an invalid token.
        """
        with pytest.raises(InvalidJWTError) as exc:
            self.jwt_handler.verify_token(VALID_REFRESH_TOKEN + "1")
        assert str(exc.value) == "Invalid JWT token"
