import datetime
from unittest import TestCase, mock

from src.auth import AuthenticationHandler

with open("test/keys/jwt-key", "r") as f:
    PRIVATE_KEY = f.read()

with open("test/keys/jwt-key.pub", "r") as f:
    PUBLIC_KEY = f.read()


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
    return MockResponse({"code": "SESSION", "message": "Unable to find user by sessionid: b764cb14-aba7-4ce1-a90e-74074dd3fe42"}, 403)


def mock_datetime_now(*args, **kwargs):
    return datetime.datetime(2020, 1, 8)


refreshed_access_token = ("eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzZXNzaW9uSWQiOiJ0ZXN0IiwidXNlcm5hbWUiOiJ0ZXN0IG5hbWUiLCJ1c2VySXNBZG1pbiI6ZmFsc2UsImV4cCI6MTU3ODQ0MTkwMH0.ew2pVkjd1YD3gha-kjw50lrtqMyhxZZT6nwYzQXM7PfjykjvhJRWS6wUXeYSeT8lGwLLZDXdaLY3nCMM8UK6ERckIvte2-BFFx12h4ZktWMLcN0tSRaKJU6mp3wrHTlVQ-iEQOtQ1GOYeZdryGbjotrq3IdRY2iuOpmTGqSRhSuAO262BEPpUxm-bgUqE9V7j9lnSRBA_GZ0OPssxOmnKrXqVoyi3zmrAcWf-Ci409JPmdrczPy6dBABHt8ayuqtY3nc8jtB45N9o97_mvfbeP2Vsf4ndFt7i5mOhib1Ytgj_TZaB1_aErBBk3VAq9uKgb9EIEJSFFj2es_kMjmCkPKRP-Bpm_caIp5Agopoocg6vc4iUnRRpJGPWSJNcBeWDoI_8aC03MME9gIuqrCRdeXJyjRRl4pEDkdi2QchV2rm1miD6uRy-ho4jBGydiylA-yZCPexnyT13Pxom63c2WqX0muHTHGD3kMCkoO0RN_aF2s5kkKkvVrRHuk2_MNg1KX03mZ1jMp3y6KNHXJuY6REZqUtufVvVNxjx-AZJajw2EkmfTMCtldtAwc54EL-i7rFc9CmIbiXFsEZK1oKyj8WOqLtN_b-DVdrzx5D6s7SNlDu9ahhdzSII2CL3_QzJNJlOiCI3dfp73L9CmMZoPz5CJiRxnwzOfitVScoOX4")
valid_access_token = ("eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzZXNzaW9uSWQiOiJ0ZXN0IiwidXNlcm5hbWUiOiJ0ZXN0IG5hbWUiLCJ1c2VySXNBZG1pbiI6ZmFsc2UsImV4cCI6OTk5OTk5OTk5OX0.ZrvLcWueXfix-dOtuFWdpZuUZAM8WrhtqUffEfZhLJPDbCe-I_D3Bcikznhtkb1k8-Kcj9MiLdUcaFXT-SvyYpc_c2Zj690FMVqfrR9yjaGGWG-2Lx2izedjSFoNu7zT779hmDanzTFNtLzSZeSU8GhXXSsrzgY2FwcDMNHiCcKb6JlcsrmSRIKQCiKK4k_VadJ7e7EioCN9tVAGiORwOy81r1m5RqSui6y8SvYzTFXSbDwjTErTVUfdIsUcN9_i_WEMn1sPztVPeQ_0o3sW0XsIxK-peuiqAqnX67OQpNQtUoMd_RtY603U9zdGujCDW-zYz-vIzWhUu5GNyFaA_1zJIuS-Ga3gGS-QXrLTYrosBTCpK0OCZp8mM4Guue7obKa5zeEL-Cq2-WlrLuPMlxCPrPH1qu_pMtYO-yaMIrfX6Xt7g-0p2ZQVIaR-vesXJC6MTIO-bqq8rIv7ToImf774gY2Fg5EiNnhkJAml8AaKfSynWsRoV7YsXoCnlqGLCwE4-RyRoq-rmm4ms1zEzwl38ydPWUzNqQMTkwqj5eYsRw-ncfVssnP0VcZ5HCcHIXKHOVuHrxqc5wJg-MkhCfJazOb8pjyDZg6fW4Omsr54Rthz3R7jeska0AbinZzAlPJSwdx9ouPxvdAD2hWxAPnp9Ii16gn50V38eMLm3wA")
expired_access_token = ("eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzZXNzaW9uSWQiOiJ0ZXN0IiwidXNlcm5hbWUiOiJ0ZXN0IG5hbWUiLCJ1c2VySXNBZG1pbiI6ZmFsc2UsImV4cCI6MTU3ODQ0MTU5OX0.cZh9eezkKpuUhx49NQORXm9Nq6VaMNA9hI_XtRlwr9wO2RkX6g4DE0I9ls9QDp8mNs1ZrKolM1aAa-3xi6GiHQBK9hQFSVZK8UYd_wG4AbnuBUmWypSKB3AD_fUtNeCv1NxOdKQPbx6CgKguWN3DmjAFrc84nrrX-FHGx5IsmiD_TeSudqBHiG7Kqbn4FWhVmyzcwTs4d0eCtTpJNGaLcNNp5WuR8GX0CnCZdgM6eFM8pvoAZGJ_lXEQ3ayCY-4CShWinAa2G1x_mwgd0-y5KhmjU1DdY6G0qqlmeFBO4Qz6LSoEjp5KHiSTSRNLVr9FIHYJY5v2MhZ9Jt-bp3e7mDEyR8M8RtnVRGAtn_KKovh0e5v2AgFnUsOVYtj3g_gr5lbiwpVY9cNa24HJqPxSb9WnjBLWYHcyhLCZKDTtZ0xdCDeQrO772rCpfb2tSif6LijQJRuhJzvjdcHJgZNeFDoF0bGha_brqRqOo4ayIn-BrfuBmN4ShplLs_Q_vGg76do7Px1QVc4_1mrXgIdl9xDCtv-z80E7Y6LzEPtEGwfoyqLJWhyF5HRYIUgJSakK6ZtZsFGMIC3uCCMZGD5KZDUcc_UKZOIZZ9mlDXyPkIehZ1AoQszZKJbkvoDf9xYLQLpdf7-0vIIhqqaIM2VjOmKD-BQjUvrfyd-Olv_sPAw")
new_refresh_token = ("eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJleHAiOjE1NzkwNDY0MDB9.pAQEve08F-fDXHZO4YeHziqO9MesmISs2LRZUTUGJHBCoJcB5tTpSgHq-XMhKkA4iVPmsN1sQ5rD6Ahr9wvKLQLTqMgDf-Gc7AVIDZ79I1D74o1wDUMEC5WUll9sUtcUuImAl2KQHWK-i74uOkZGv7ibzGZFMREoW9KApA9yCc15KeZgSF9XoKxyAkr2T1WYH2kzT9DRUn5ddZgjDJHjlJhUuZUSdDqAXKT4dYZabP48xZmjSBrnr7MdoS5x2jhmanBIWFtbuuAK1L9MRd0uY1RAcrueUjoDEfjoT56R9nju4rcRL5QGaArJSQpNEel-mxqHqEZpjE3Me1AGjUFT494v95Rg2KG2aFGIfxcMMaEd5dNU2BlhGlviQK5KDuLuBULra_0aiFm8TRVHjTWE9uIKI0ZS5Vzl4umu3c1YAbWXAolBxXoH8tYnuvVYI-HCdwd7f_B1BPrAmPBhSRLaBrQwqU_EJtit5XSi9Pm4Y-c93EmzT0sFZk9Z8-xjw0Sr2hbNwGsd5gSN_YPUZH-r9XZ6xy1a9HRVKS0UVWq2P5oSHtrafl95OZ_WbSd4Hh0cOnuf6chz4AWM6JP-tlOYMas5D387a9el0Pl3nl3xO9pk7oUATeeMlm1Vx2nt7bvsbgQwBhfY5OnGrW9reem1zZTEm4SpJTraKLleGh1UGd8")
valid_refresh_token = ("eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJleHAiOjk5OTk5OTk5OTl9.dgakoOk09sfdjTpPvC28RQbmJFt_F2eWq4AuBGyp9Z6ri1XHycRNiv-4ewixw_uZaD57Y_Xr5tJuoSlUEfVL0f2R-X-AHhGb1aYsY6Gk0hIBupYkLM-sEOQNLGffK7ayd58k8ay_GtjxuLcmsqqBdCWYM3nr0JCDpsnBYaRXFvHQKThOk7BEJPFmlEk06w0C8OW35GDn9EPl_ArKKyUDm2H1Wbgjn7mVrVmpcoUyXmaDMJ63ZOMvm82j-3y2H2Bye0Ezlc2h4DLPH9KB3CuwdArwaka_ybA8_DVah4poWvZXxS3vNS5cLBGnKPwRSjo4VHcgilpqeM63nrelfqjEg2MP5-CDnUro0MrtoHg1VoF0zLTFuDrdx4YkD---uML0e3K8_UhCG1ipj-WwA9oUpQ0SEZ8KnlNKXRxutuyei3U7Q9c60Joye7sldmAVWDL6W8EnUPyGKAYyMSWDbzHANzHCAaBl5GJSuiiHFyjVli9PFJJPcwJb4hXZybjaPNsmeiHnZUPCY_ESuyFQYJpo4Ot5rbYabBkVVvTz5BK3RXVAwecxEGrzsRyl_vLOKn_D1T6_gQkHmPI99ySDNIo7qL7N9P5aLxwJTGYl9xczsQtuUXe1PurjQSj78b4ioU8ImPC1AYwGJzRHDgeM3q04nx3tFPOwLmOdRZwEBmcGXWk")
expired_refresh_token = ("eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJleHAiOjEwMDAwMDAwMDB9.SWuznEIymHglPP4rSNjlVjY5kAwNKQEgiVsXxItxCgrdhNCrhadKLYTV0EFs3oEfylCSpkrQF1nfhlXhOhuUVvWQJR6itxVDxMfyS_YkDSLyrdeiEbpYcQ-dNv7mPKdPOdcwqnh_f0w5Fg961zoGAYLxpdCN67hvIkW1RXMX4n8ZGV_kQ9vdLpg3Jx4x29iSzAKF5ZBdocwUZZaYojpVdsIvv3cdoxS0LRShgKowYwdyKp8xWVacV8wS4stUh9rpk70MSVjlec4ecAaDqMxI0WyO3bVxtXsKj9bGlbzyUvhxEMRFyuyYtpMIXspuvblqqDJZkCiMqbrJxtJxXirNzwJYqKwgsjJxzrcsJygWi4GnVUykaOvvIznZ9iJmaVsMFrXDjLhQDxsoRAQuodpHdE4tWzpXWSQgMLHscjvFqfIgybX0JQCeOXMtXVgIj3Y8a2MvsmEYMmqwypYyRLrF4LsjTi9A9vu3Zo5RU5Lbwqbwvp-Auan-_4Ef5aBKgYCa1CaMP-nRZMMz8esdeEwx_xQ21FX1zZt-VMt-bC_J-b_9Ym7gpizvi-nrymF-yNLS8HF519NM1TlV0H_4Kc4uI6WESlGcM9TyEMh8yoy2tMMzURyahy8h98hIG5H0sP1fadZ_RdYxhqR79VDISxugVcXmdltMlMRmFrRSwf1ENXk")


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
    def test_get_access_token(self, mock_post, mock_get, mock_now):
        self.handler.set_mnemonic("anon")
        token = self.handler.get_access_token()
        expected_token = refreshed_access_token
        self.assertEqual(token, expected_token)

    def test_verify_token_success(self):
        token = valid_access_token
        result = self.handler.verify_token(token)
        self.assertEqual(result, ("", 200))

    def test_verify_token_error(self):
        token = expired_access_token
        result = self.handler.verify_token(token)
        self.assertEqual(result, ("Unauthorized", 403))

    @mock.patch("src.auth.current_time", side_effect=mock_datetime_now)
    def test_get_refresh_token(self, mock_now):
        token = self.handler.get_refresh_token()
        expected_token = new_refresh_token
        self.assertEqual(token, expected_token)

    @mock.patch("requests.put", side_effect=mock_session_put_request_success)
    @mock.patch("src.auth.current_time", side_effect=mock_datetime_now)
    def test_refresh_token_success(self, mock_put, mock_now):
        refresh_token = valid_refresh_token
        access_token = expired_access_token
        result = self.handler.refresh_token(refresh_token, access_token)
        expected_access_token = refreshed_access_token
        self.assertEqual(result, (expected_access_token, 200))

    def test_refresh_token_error_expired_refresh_token(self):
        refresh_token = expired_refresh_token
        access_token = refreshed_access_token
        result = self.handler.refresh_token(refresh_token, access_token)
        self.assertEqual(result, ("Refresh token was not valid", 403))

    @mock.patch("src.auth.BLACKLIST", [valid_refresh_token])
    def test_refresh_token_error_blacklisted_refresh_token(self):
        refresh_token = valid_refresh_token
        access_token = refreshed_access_token
        result = self.handler.refresh_token(refresh_token, access_token)
        self.assertEqual(result, ("Refresh token was not valid", 403))

    @mock.patch("requests.put", side_effect=mock_session_put_request_failure)
    @mock.patch("src.auth.current_time", side_effect=mock_datetime_now)
    def test_refresh_token_error_access_token_refresh_failure(self, mock_put, mock_now):
        refresh_token = valid_refresh_token
        access_token = refreshed_access_token
        result = self.handler.refresh_token(refresh_token, access_token)
        self.assertEqual(result, ("Unable to refresh token", 403))
