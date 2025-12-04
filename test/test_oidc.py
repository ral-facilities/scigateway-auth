"""
Unit tests for the `oidc` module.
"""

import time
from unittest.mock import Mock, patch

from cryptography.hazmat.primitives import serialization
import jwt
import pytest
import requests

from scigateway_auth.common.exceptions import InvalidJWTError, OidcProviderNotFoundError
from scigateway_auth.src import oidc
from test.mock_data import JWK_PRIVATE_KEY, JWK_PUBLIC


MOCK_CONFIGURATION = {
    "issuer": "https://mock-oidc-provider/issuer",
    "jwks_uri": "https://mock-oidc-provider/issuer/keys",
    "token_endpoint": "https://mock-oidc-provider/issuer/token",
}

MOCK_JWKS = {"keys": [JWK_PUBLIC]}


class MockRequestsResponse:

    def __init__(self, json):
        self._json = json

    def raise_for_status(self):
        pass

    def json(self):
        return self._json


def mock_requests_get(url: str, **kwargs):

    if url == "https://mock-oidc-provider/.well-known/openid-configuration":
        return MockRequestsResponse(MOCK_CONFIGURATION)

    if url == "https://mock-oidc-provider/issuer/keys":
        return MockRequestsResponse(MOCK_JWKS)

    raise requests.ConnectionError


def mock_requests_post(url: str, **kwargs):

    if url == "https://mock-oidc-provider/issuer/token":
        return MockRequestsResponse({"token_type": "Bearer", "id_token": create_token()})

    raise requests.ConnectionError


def create_payload():
    return {
        "sub": "test-username",
        "iss": "https://mock-oidc-provider/issuer",
        "aud": "5041ee0190fa",
        "iat": int(time.time()),
        "exp": int(time.time()) + 600,
    }


def create_token(payload=None, headers=None):
    if headers is None:
        headers = {"kid": "mock-kid"}

    if payload is None:
        payload = create_payload()

    private_key = serialization.load_pem_private_key(JWK_PRIVATE_KEY.encode(), None)
    return jwt.encode(payload, private_key, algorithm="RS256", headers=headers)


class TestOidc:
    """
    Test suite for the `oidc` module
    """

    @patch("requests.get")
    def test_get_username(self, mock_get: Mock):
        """
        Test that oidc.get_username() return the expected mechanism and username.
        """
        mock_get.side_effect = mock_requests_get

        mechanism, username = oidc.get_username("mock-pkce", create_token())
        assert mechanism is None
        assert username == "test-username"

    @patch("requests.get")
    def test_get_username_expired(self, mock_get: Mock):
        """
        Test that oidc.get_username() raises InvalidJWTError if exp is missing or expired.
        """
        mock_get.side_effect = mock_requests_get

        payload = create_payload()
        payload["exp"] = int(time.time()) - 10

        with pytest.raises(InvalidJWTError):
            mechanism, username = oidc.get_username("mock-pkce", create_token(payload))

        del payload["exp"]

        with pytest.raises(InvalidJWTError):
            mechanism, username = oidc.get_username("mock-pkce", create_token(payload))

    @patch("requests.get")
    def test_get_username_invalid_audience(self, mock_get: Mock):
        """
        Test that oidc.get_username() raises InvalidJWTError if aud is missing or isn't the expected value.
        """
        mock_get.side_effect = mock_requests_get

        payload = create_payload()
        payload["aud"] = "invalid"

        with pytest.raises(InvalidJWTError):
            mechanism, username = oidc.get_username("mock-pkce", create_token(payload))

        del payload["aud"]

        with pytest.raises(InvalidJWTError):
            mechanism, username = oidc.get_username("mock-pkce", create_token(payload))

    @patch("requests.get")
    def test_get_username_invalid_issuer(self, mock_get: Mock):
        """
        Test that oidc.get_username() raises InvalidJWTError if iss is missing or isn't the expected value.
        """
        mock_get.side_effect = mock_requests_get

        payload = create_payload()
        payload["iss"] = "invalid"

        with pytest.raises(InvalidJWTError):
            mechanism, username = oidc.get_username("mock-pkce", create_token(payload))

        del payload["iss"]

        with pytest.raises(InvalidJWTError):
            mechanism, username = oidc.get_username("mock-pkce", create_token(payload))

    @patch("requests.get")
    def test_get_username_missing_sub(self, mock_get: Mock):
        """
        Test that oidc.get_username() raises InvalidJWTError if sub is missing.
        """
        mock_get.side_effect = mock_requests_get

        payload = create_payload()
        del payload["sub"]

        with pytest.raises(InvalidJWTError):
            mechanism, username = oidc.get_username("mock-pkce", create_token(payload))

    @patch("requests.get")
    def test_get_username_missing_kid(self, mock_get: Mock):
        """
        Test that oidc.get_username() raises InvalidJWTError if kid is missing.
        """
        mock_get.side_effect = mock_requests_get

        with pytest.raises(InvalidJWTError):
            mechanism, username = oidc.get_username("mock-pkce", create_token(headers={}))

    @patch("requests.get")
    def test_get_username_unkonwn_key(self, mock_get: Mock):
        """
        Test that oidc.get_username() raises InvalidJWTError if kid doesn't match a key from the JWKS.
        """
        mock_get.side_effect = mock_requests_get

        with pytest.raises(InvalidJWTError):
            mechanism, username = oidc.get_username("mock-pkce", create_token(headers={"kid": "unknown"}))

    @patch("requests.get")
    def test_get_username_unkown_provider(self, mock_get: Mock):
        """
        Test that oidc.get_username() raises OidcProviderNotFoundError if the provider_id is not found.
        """
        mock_get.side_effect = mock_requests_get

        with pytest.raises(OidcProviderNotFoundError):
            mechanism, username = oidc.get_username("unknown", create_token())

    @patch("requests.post")
    @patch("requests.get")
    def test_get_token(self, mock_get: Mock, mock_post: Mock):
        """
        Test that oidc.get_token() works.
        """
        mock_get.side_effect = mock_requests_get
        mock_post.side_effect = mock_requests_post

        oidc.get_token("mock-client-secret", "test-code")

    @patch("requests.post")
    @patch("requests.get")
    def test_get_token_no_client_secret(self, mock_get: Mock, mock_post: Mock):
        """
        Test that oidc.get_token() raises OidcProviderNotFoundError if the OIDC provider has no client_secret.
        """
        mock_get.side_effect = mock_requests_get
        mock_post.side_effect = mock_requests_post

        with pytest.raises(OidcProviderNotFoundError):
            oidc.get_token("mock-pkce", "test-code")
