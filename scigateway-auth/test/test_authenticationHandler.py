from unittest import TestCase, mock

from src.auth import AuthenticationHandler
import datetime

class MockResponse(object):
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

def mock_post_requests(*args, **kwargs):
    return MockResponse({"sessionId": "test"}, 200)

def mock_session_put_request_success(*args, **kwargs):
    return MockResponse("", 204)

def mock_session_put_request_failure(*args, **kwargs):
    return MockResponse({"code":"SESSION","message":"Unable to find user by sessionid: b764cb14-aba7-4ce1-a90e-74074dd3fe42"}, 403)

def mock_datetime_now(*args, **kwargs):
    return datetime.datetime(2020, 1, 8)

@mock.patch("src.auth.ACCESS_TOKEN_VALID_FOR", 5)
@mock.patch("src.auth.REFRESH_TOKEN_VALID_FOR", 10080)
class TestAuthenticationHandler(TestCase):
    def setUp(self):
        self.handler = AuthenticationHandler()

    def test__pack_jwt(self):
        token = self.handler._pack_jwt({"test": "test"})
        expected_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0ZXN0IjoidGVzdCJ9.7hcgHX1vqTX8pc85fMpAA4Mdc3vAiuyInHaamnEnJLM"
        self.assertEqual(token, expected_token)

    @mock.patch("requests.post", side_effect=mock_post_requests)
    @mock.patch("src.auth.current_time", side_effect=mock_datetime_now)
    def test_get_access_token(self, mock_get, mock_now):
        self.handler.set_mnemonic("anon")
        token = self.handler.get_access_token()
        expected_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzZXNzaW9uSWQiOiJ0ZXN0IiwiZXhwIjoxNTc4NDQxOTAwfQ.Fb6XjGfjf0IAWo8ndGnbbP_iHhUxtj-x6adg391LUPc"
        self.assertEqual(token, expected_token)

    def test_verify_token_success(self):
        token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0ZXN0IjoidGVzdCJ9.7hcgHX1vqTX8pc85fMpAA4Mdc3vAiuyInHaamnEnJLM"
        result = self.handler.verify_token(token)
        self.assertEqual(result, ("", 200))

    def test_verify_token_error(self):
        token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzZXNzaW9uSWQiOiJ0ZXN0IiwiZXhwIjoxNTc4NDQxOTAwfQ.Fb6XjGfjf0IAWo8ndGnbbP_iHhUxtj-x6adg391LUPc"
        result = self.handler.verify_token(token)
        self.assertEqual(result, ("Unauthorized", 403))

    @mock.patch("src.auth.current_time", side_effect=mock_datetime_now)
    def test_get_refresh_token(self, mock_now):
        token = self.handler.get_refresh_token()
        expected_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1NzkwNDY0MDB9.K9euULOF1pgWqjT6QVNufnUkapeoSwGnwiasGbHXR64"
        self.assertEqual(token, expected_token)

    @mock.patch("requests.put", side_effect=mock_session_put_request_success)
    @mock.patch("src.auth.current_time", side_effect=mock_datetime_now)
    def test_refresh_token_success(self, mock_put, mock_now):
        refresh_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjk5OTk5OTk5OTl9.-uzIkAKdwAovyjV1ICaLT8G5WGxG5rJ5SLTBSOHMaP0"
        access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzZXNzaW9uSWQiOiJ0ZXN0IiwiZXhwIjoxNTc4NDQxOTAwfQ.Fb6XjGfjf0IAWo8ndGnbbP_iHhUxtj-x6adg391LUPc"
        result = self.handler.refresh_token(refresh_token, access_token)
        expected_access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzZXNzaW9uSWQiOiJ0ZXN0IiwiZXhwIjoxNTc4NDQxOTAwfQ.Fb6XjGfjf0IAWo8ndGnbbP_iHhUxtj-x6adg391LUPc"
        self.assertEqual(result, (expected_access_token, 200))

    def test_refresh_token_error_expired_refresh_token(self):
        refresh_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjEwMDAwMDAwMDB9.MzszsXjd6dS0at0MeZ81FgqWcqyV6zznxJ_1Fpoy-20"
        access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzZXNzaW9uSWQiOiJ0ZXN0IiwiZXhwIjoxNTc4NDQxOTAwfQ.Fb6XjGfjf0IAWo8ndGnbbP_iHhUxtj-x6adg391LUPc"
        result = self.handler.refresh_token(refresh_token, access_token)
        self.assertEqual(result, ("Refresh token was not valid", 403))

    @mock.patch("src.auth.BLACKLIST", ["eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjk5OTk5OTk5OTl9.-uzIkAKdwAovyjV1ICaLT8G5WGxG5rJ5SLTBSOHMaP0"])
    def test_refresh_token_error_blacklisted_refresh_token(self):
        refresh_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjk5OTk5OTk5OTl9.-uzIkAKdwAovyjV1ICaLT8G5WGxG5rJ5SLTBSOHMaP0"
        access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzZXNzaW9uSWQiOiJ0ZXN0IiwiZXhwIjoxNTc4NDQxOTAwfQ.Fb6XjGfjf0IAWo8ndGnbbP_iHhUxtj-x6adg391LUPc"
        result = self.handler.refresh_token(refresh_token, access_token)
        self.assertEqual(result, ("Refresh token was not valid", 403))

    @mock.patch("requests.put", side_effect=mock_session_put_request_failure)
    @mock.patch("src.auth.current_time", side_effect=mock_datetime_now)
    def test_refresh_token_error_access_token_refresh_failure(self, mock_put, mock_now):
        refresh_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjk5OTk5OTk5OTl9.-uzIkAKdwAovyjV1ICaLT8G5WGxG5rJ5SLTBSOHMaP0"
        access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzZXNzaW9uSWQiOiJ0ZXN0IiwiZXhwIjoxNTc4NDQxOTAwfQ.Fb6XjGfjf0IAWo8ndGnbbP_iHhUxtj-x6adg391LUPc"
        result = self.handler.refresh_token(refresh_token, access_token)
        self.assertEqual(result, ("Unable to refresh token", 403))
