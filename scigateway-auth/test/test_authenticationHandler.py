from unittest import TestCase, mock

from src.auth import AuthenticationHandler

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


class TestAuthenticationHandler(TestCase):
    def setUp(self):
        self.handler = AuthenticationHandler()

    def test__pack_jwt(self):
        token = self.handler._pack_jwt({"test": "test"})
        expected_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0ZXN0IjoidGVzdCJ9.7hcgHX1vqTX8pc85fMpAA4Mdc3vAiuyInHaamnEnJLM"
        self.assertEqual(token, expected_token)

    @mock.patch("requests.post", side_effect=mock_post_requests)
    @mock.patch("requests.get", side_effect=mock_get_requests)
    def test_get_jwt(self, mock_post ,mock_get):
        self.handler.set_mnemonic("anon")
        token = self.handler.get_jwt()
        expected_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzZXNzaW9uSWQiOiJ0ZXN0IiwidXNlcm5hbWUiOiJ0ZXN0IG5hbWUifQ.cvuZAxlsvPCc2_43SW5BFPEBeERc0idJhVV8pCIgCnk"
        self.assertEqual(token, expected_token)


