import datetime
from unittest import TestCase, mock

from src.auth import AuthenticationHandler
from test.testutils import PRIVATE_KEY, PUBLIC_KEY, REFRESHED_ACCESS_TOKEN, \
    REFRESHED_NON_ADMIN_ACCESS_TOKEN, VALID_ACCESS_TOKEN, EXPIRED_ACCESS_TOKEN, NEW_REFRESH_TOKEN, \
    VALID_REFRESH_TOKEN, EXPIRED_REFRESH_TOKEN


class MockResponse(object):
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


def mock_post_requests(*args, **kwargs):
    return MockResponse({"sessionId": "test"}, 200)


def mock_get_requests(*args, **kwargs):
    return MockResponse({"userName": "test name", "remainingMinutes": 60}, 200)


def mock_session_put_request_success(*args, **kwargs):
    return MockResponse("", 204)


def mock_session_put_request_failure(*args, **kwargs):
    return MockResponse({"code": "SESSION",
                         "message": "Unable to find user by sessionid: "
                                    "b764cb14-aba7-4ce1-a90e-74074dd3fe42"},
                        403)


def mock_datetime_now(*args, **kwargs):
    return datetime.datetime(2020, 1, 8)


@mock.patch("src.auth.ACCESS_TOKEN_VALID_FOR", 5)
@mock.patch("src.auth.REFRESH_TOKEN_VALID_FOR", 10080)
@mock.patch("src.auth.PRIVATE_KEY", PRIVATE_KEY)
@mock.patch("src.auth.PUBLIC_KEY", PUBLIC_KEY)
class TestAuthenticationHandler(TestCase):
    def setUp(self):
        self.handler = AuthenticationHandler()

    def test__pack_jwt(self):
        token = self.handler._pack_jwt({"test": "test"})
        expected_token = ("eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ0ZXN0IjoidGV"
                          "zdCJ9.aCqysXBRNgBakmUa3NCksATw_CsNYkLU_AQoDl3DYTCFaIpEjJGzw-qfKkydLnQa"
                          "MK01WHdWqMrx9lft9RWSCGstNJAS1QzyVTNRcvIYGFo4GaCU8mtDuP94kCpWK-VXZmXmIg"
                          "z5pTszMfRs0vmfWQIahHrDbGfY_h36BycMgUwZH9VE1OeX0KaMmQHjIaG0-dUUEDO0XqSh"
                          "Rny6Ml2qdhQ0bE3oxM4pC8HCgb-sMQXdSImun1X4lSetRdjOcdJVDJZkV8eiN9xda9VYRn"
                          "lWZSmAR4j8IiF5sE9It5x-snSDwnAUfm_kfiPYROeUuZQNBv0db9B1GFdT9sFeoZjs6eap"
                          "nhWHwEMhVJVp7OkmSkDFimyPyXNGNq8LRY6UxonyWfzjHLvBvYSfZJBC4yye5zetj-Pc8u"
                          "frKrU7wXiHtkXiwxKk0rCQBe6LEvS8AGmNTZFa3olLEyzb_VgLSaFHDdSogFXAaDnBHWMc"
                          "Mr-77c35m6iW2WB2-FreedL5tbKw1MM51S0WFe9lVeGzsYx5fxG048iIuusLXg0AyORIVA"
                          "Q-2LDK1fX3VmKVULMOJdCsPIhwK8W9HUKPWlSqBEeITkEDkohCxGHHL2iOFQS52PGGfMzx"
                          "9ix8pa_MzPtC0MR1LfxnGNi8F5PUAE34yRi7ha3yA5J2ocMLeVl9lQ7M6ms")
        self.assertEqual(token, expected_token)

    @mock.patch("requests.post", side_effect=mock_post_requests)
    @mock.patch("requests.get", side_effect=mock_get_requests)
    @mock.patch("src.auth.current_time", side_effect=mock_datetime_now)
    @mock.patch("src.auth.ADMIN_USERS", ['test name'])
    def test_get_access_token_admin_user(self, mock_post, mock_get, mock_now):
        self.handler.set_mnemonic("anon")
        token = self.handler.get_access_token()
        expected_token = REFRESHED_ACCESS_TOKEN
        self.assertEqual(token, expected_token)

    @mock.patch("requests.post", side_effect=mock_post_requests)
    @mock.patch("requests.get", side_effect=mock_get_requests)
    @mock.patch("src.auth.current_time", side_effect=mock_datetime_now)
    def test_get_access_token_non_admin_user(self, mock_post, mock_get, mock_now):
        self.handler.set_mnemonic("anon")
        token = self.handler.get_access_token()
        expected_token = REFRESHED_NON_ADMIN_ACCESS_TOKEN
        self.assertEqual(token, expected_token)

    def test_verify_token_success(self):
        token = VALID_ACCESS_TOKEN
        result = self.handler.verify_token(token)
        self.assertEqual(result, ("", 200))

    def test_verify_token_error(self):
        token = EXPIRED_ACCESS_TOKEN
        result = self.handler.verify_token(token)
        self.assertEqual(result, ("Unauthorized", 403))

    @mock.patch("src.auth.current_time", side_effect=mock_datetime_now)
    def test_get_refresh_token(self, mock_now):
        token = self.handler.get_refresh_token()
        expected_token = NEW_REFRESH_TOKEN
        self.assertEqual(token, expected_token)

    @mock.patch("requests.put", side_effect=mock_session_put_request_success)
    @mock.patch("src.auth.current_time", side_effect=mock_datetime_now)
    def test_refresh_token_success(self, mock_put, mock_now):
        refresh_token = VALID_REFRESH_TOKEN
        access_token = EXPIRED_ACCESS_TOKEN
        result = self.handler.refresh_token(refresh_token, access_token)
        expected_access_token = REFRESHED_NON_ADMIN_ACCESS_TOKEN
        self.assertEqual(result, (expected_access_token, 200))

    def test_refresh_token_error_EXPIRED_REFRESH_TOKEN(self):
        refresh_token = EXPIRED_REFRESH_TOKEN
        access_token = REFRESHED_ACCESS_TOKEN
        result = self.handler.refresh_token(refresh_token, access_token)
        self.assertEqual(result, ("Refresh token was not valid", 403))

    @mock.patch("src.auth.BLACKLIST", [VALID_REFRESH_TOKEN])
    def test_refresh_token_error_blacklisted_refresh_token(self):
        refresh_token = VALID_REFRESH_TOKEN
        access_token = REFRESHED_ACCESS_TOKEN
        result = self.handler.refresh_token(refresh_token, access_token)
        self.assertEqual(result, ("Refresh token was not valid", 403))

    @mock.patch("requests.put", side_effect=mock_session_put_request_failure)
    @mock.patch("src.auth.current_time", side_effect=mock_datetime_now)
    def test_refresh_token_error_access_token_refresh_failure(self, mock_put, mock_now):
        refresh_token = VALID_REFRESH_TOKEN
        access_token = REFRESHED_ACCESS_TOKEN
        result = self.handler.refresh_token(refresh_token, access_token)
        self.assertEqual(result, ("Unable to refresh token", 403))
