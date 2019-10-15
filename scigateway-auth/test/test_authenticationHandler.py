from unittest import TestCase, mock

from src.auth import AuthenticationHandler


def mock_post_requests(*args, **kwargs):
    class MockResponse(object):
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    return MockResponse({"session_id": "test"}, 200)


class TestAuthenticationHandler(TestCase):
    def setUp(self):
        self.handler = AuthenticationHandler()

    def test__pack_jwt(self):
        token = self.handler._pack_jwt({"test": "test"})
        expected_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0ZXN0IjoidGVzdCJ9.7hcgHX1vqTX8pc85fMpAA4Mdc3vAiuyInHaamnEnJLM"
        self.assertEqual(token, expected_token)

    @mock.patch("requests.post", side_effect=mock_post_requests)
    def test_get_jwt(self, mock_get):
        token = self.handler.get_jwt()
        expected_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzZXNzaW9uX2lkIjoidGVzdCJ9.8WxX7mlf1rrIcHqUyDXQMz5hsrsE-w3957U6Sqf06vc"
        self.assertEqual(token, expected_token)


