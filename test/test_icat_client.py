"""
Unit tests for the `ICATClient` class.
"""

from unittest.mock import Mock, patch

import pytest

from scigateway_auth.common.config import config
from scigateway_auth.common.exceptions import ICATServerError, InvalidCredentialsError
from scigateway_auth.common.schemas import UserCredentialsPostRequestSchema
from scigateway_auth.src.icat_client import ICATClient


class TestICATClient:
    """
    Test suite for the `ICATClient` class.
    """

    username = "test-username"
    password = "test-password"  # noqa: S105
    mnemonic = "test-mnemonic"
    session_id = "test-session-id"
    credentials = UserCredentialsPostRequestSchema(username=username, password=password)
    user_instrument_ids = [1, 3, 5]
    user_investigation_ids = [2, 4, 6, 8, 10]

    def create_mock_response(self, status_code: int, json_data: dict | list = None) -> Mock:
        """
        Helper function to create a mock response with a given status code and JSON data.

        :param status_code: The HTTP status code to simulate.
        :param json_data: The JSON data to return in the mock response.
        :return: A mock object mimicking an HTTP response.
        """
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.json.return_value = json_data
        return mock_response

    @patch("requests.post")
    def test_authenticate_success(self, mock_post):
        """
        Test that `authenticate` method successfully returns a session ID when authentication is successful.
        """
        mock_post.return_value = self.create_mock_response(200, {"sessionId": self.session_id})
        session_id = ICATClient.authenticate(self.mnemonic, self.credentials)
        assert session_id == self.session_id

    @patch("requests.post")
    def test_authenticate_failure(self, mock_post):
        """
        Test that `authenticate` method raises an `ICATServerError` on authentication failure.
        """
        json_data = {"code": "SESSION", "message": "Error logging in. Please try again later"}
        mock_post.return_value = self.create_mock_response(400, json_data)
        with pytest.raises(ICATServerError) as exc:
            ICATClient.authenticate(self.mnemonic, self.credentials)
        assert str(exc.value) == json_data["message"]

    @patch("requests.post")
    def test_authenticate_invalid_credentials(self, mock_post):
        """
        Test that `authenticate` method raises an `ICATServerError` on authentication failure.
        """
        json_data = {"code": "SESSION", "message": "The username and password do not match "}
        mock_post.return_value = self.create_mock_response(403, json_data)
        with pytest.raises(InvalidCredentialsError) as exc:
            ICATClient.authenticate(self.mnemonic, self.credentials)
        assert str(exc.value) == json_data["message"]

    @patch("requests.get")
    def test_get_username_success(self, mock_get):
        """
        Test that `get_username` method successfully returns the username when provided a valid session ID.
        """
        mock_get.return_value = self.create_mock_response(200, {"userName": self.username, "remainingMinutes": 60})
        username = ICATClient.get_username(self.session_id)
        assert username == self.username

    @patch("requests.get")
    def test_get_username_failure(self, mock_get):
        """
        Test that `get_username` method raises an `ICATServerError` when the session ID is invalid.
        """
        json_data = {"code": "SESSION", "message": f"Unable to find user by sessionid: {self.username}"}
        mock_get.return_value = self.create_mock_response(400, json_data)
        with pytest.raises(ICATServerError) as exc:
            ICATClient.get_username("mocked_session_id")
        assert str(exc.value) == json_data["message"]

    @patch("requests.get")
    def test_get_authenticators(self, mock_get):
        """
        Test that `get_authenticators` method returns a list of authenticators when the request is successful.
        """
        json_data = {"authenticators": [{"mnemonic": "anon", "keys": []}]}
        mock_get.return_value = self.create_mock_response(200, json_data)
        authenticators = ICATClient.get_authenticators()
        assert authenticators == json_data["authenticators"]

    @patch("requests.put")
    def test_refresh_success(self, mock_put):
        """
        Test that `refresh` method successfully completes without errors when the session ID is valid.
        """
        mock_put.return_value = self.create_mock_response(204, {})
        ICATClient.refresh(self.session_id)

        mock_put.assert_called_once_with(
            f"{config.icat_server.url}/session/{self.session_id}",
            verify=config.icat_server.certificate_validation,
            timeout=config.icat_server.request_timeout_seconds,
        )

    @patch("requests.put")
    def test_refresh_failure(self, mock_put):
        """
        Test that `refresh` method raises an `ICATServerError` when the session ID is invalid.
        """
        mock_put.return_value = self.create_mock_response(
            403,
            {"code": "SESSION", "message": "Unable to find user by sessionid: invalid-session-id"},
        )
        with pytest.raises(ICATServerError) as exc:
            ICATClient.refresh("invalid-session-id")
        assert str(exc.value) == "The session ID was unable to be refreshed"

    @patch("requests.get")
    def test_get_user_instrument_ids(self, mock_get):
        """
        Test that `get_user_instrument_ids` method returns a list of instrument IDs when the request is successful.
        """
        mock_get.return_value = self.create_mock_response(200, self.user_instrument_ids)
        user_instrument_ids = ICATClient.get_user_instrument_ids(self.session_id, self.username)
        assert user_instrument_ids == self.user_instrument_ids

    @patch("requests.get")
    def test_get_user_instrument_ids_failure(self, mock_get):
        """
        Test that `get_user_instrument_ids` method raises an `ICATServerError` when the session ID is invalid.
        """
        json_data = {"code": "SESSION", "message": "Unable to find user by sessionid: invalid-session-id"}
        mock_get.return_value = self.create_mock_response(403, json_data)
        with pytest.raises(ICATServerError) as exc:
            ICATClient.get_user_instrument_ids("invalid-session-id", self.username)
        assert str(exc.value) == json_data["message"]

    @patch("requests.get")
    def test_get_user_investigation_ids(self, mock_get):
        """
        Test that `get_user_investigation_ids` method returns a list of instrument IDs when the request is successful.
        """
        mock_get.return_value = self.create_mock_response(200, self.user_investigation_ids)
        user_instrument_ids = ICATClient.get_user_investigation_ids(self.session_id, self.username)
        assert user_instrument_ids == self.user_investigation_ids

    @patch("requests.get")
    def test_get_user_investigation_ids_failure(self, mock_get):
        """
        Test that `get_user_investigation_ids` method raises an `ICATServerError` when the session ID is invalid.
        """
        json_data = {"code": "SESSION", "message": "Unable to find user by sessionid: invalid-session-id"}
        mock_get.return_value = self.create_mock_response(403, json_data)
        with pytest.raises(ICATServerError) as exc:
            ICATClient.get_user_investigation_ids("invalid-session-id", self.username)
        assert str(exc.value) == json_data["message"]
