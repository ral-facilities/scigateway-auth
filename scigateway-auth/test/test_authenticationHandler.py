from unittest import TestCase, mock

from src.auth import AuthenticationHandler

with open("scigateway-auth/test/keys/jwt-key", "r") as f:
    PRIVATE_KEY = f.read()

def mock_post_requests(*args, **kwargs):
    class MockResponse(object):
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    return MockResponse({"sessionId": "test"}, 200)


class TestAuthenticationHandler(TestCase):
    def setUp(self):
        self.handler = AuthenticationHandler()

    @mock.patch("src.auth.PRIVATE_KEY", PRIVATE_KEY)
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
    @mock.patch("src.auth.PRIVATE_KEY", PRIVATE_KEY)
    def test_get_jwt(self, mock_private_key):
        self.handler.set_mnemonic("anon")
        token = self.handler.get_jwt()
        expected_token = ("eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzZXNzaW9uSWQ"
        "iOiJ0ZXN0In0.U7FORrpMWQ1qagquoyn6vsYvzF52qsVxWY-sf-CMzMK-SRdds0pYY6Et_"
        "wI2GncHjrw2Xa9JPkK3CvMO3BqpbOC9dwHvRrm5-PbC7o0Y56-e8F3_daljJFpOIMmiwIM"
        "-O1Gyh0BI9Eh3jXiGMRIdfmpQTFAUsguEBO8CcHS7N4Yxbsu2aYaCXHOez-BqiCrbdG8H7"
        "BAzyDOfgeEfZwEHeAQnPNm6ea06ouQFxteSdjgwdpq4zNo2nPgujMzUU5F1AG1mojqG8IU"
        "ZTKl82saFfXrODNjtWHQue86JOmDr5nyWhUspt940HuloYxnygI6CpwAmAEc_UgFJnW4E6"
        "FDOZBtq-bAN1CQenyQpSHSE3b5Wqq3glkJEXOsIWZZIreverccmJjBRiJLYGVaAuY3JZ4A"
        "AwZ9og1IQ4t2Tzeq3SUgeonWWl-vqH225MYVnQkViq2_hS3usWlt13qUaPFt99frCa4fWV"
        "CKzgNBKwoFtdFSnWStwA-WaICDa9-fkkbagyfbHdRlFTmA9OGzC8b3L3Ud3NF4lG0YDvu6"
        "9UtaeDDBilwmzI31CuX9FHeojE7ZZtBfEWLvdqtwV7oq9QGO6mgMUy2BY3HurAc_2gB-qy"
        "vH0UDSV_jB1xKxjVRsYUJwXVCfDwBsL2-_XYu-jG_k1VXHTZs4KMg-r2IqqqL6inKQ")
        self.assertEqual(token, expected_token)


