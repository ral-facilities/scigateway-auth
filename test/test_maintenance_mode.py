import json
from unittest import TestCase, mock

from src import admin
from src.admin import MaintenanceMode

with open("test/keys/jwt-key.pub", "r") as f:
    PUBLIC_KEY = f.read()
MAINTENANCE_CONFIG_PATH = "path/to/config/test_config.json"
MAINTENANCE_STATE = {"test": "test"}
VALID_ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzZXNzaW9uSWQiOiJ0ZXN0IiwidXNlcm5hbWUiOiJ0ZXN0IG5hbWUiLCJ1c2VySXNBZG1pbiI6dHJ1ZSwiZXhwIjo5OTk5OTk5OTk5fQ.L2pR4ViBiUoZtEYat8boDyfs1RgVbHQS_-MNK7-QfdA4aEzfghJjm53EeySw88zyVpiZcNgO9owu400ywPDmKu0A88i82hhltEd0zIPLd3PfCUUe4NlzZ5aNavuemrQ3FAztc9c0GIJFVBwPkItLmwyL47uTgSBJB_a5y51tVh61g_FLg3Bb7vYwyTyjxIUhrzwc4mXfpeybQae5fcQKJzE3MbZxHEtGYhL9p7ukaaFl1UnGeGba_CALD3kZBLFge50eobiDUx_RTpUHHRrOq4prtiBXZk7LH1xrBIVhEXqJX04aoS-0N7cxtJ5RUcOzLYKNAHo0eBVjIj6cly7aaz_DDEIjDQb51FvvwQBXBN33XOikABrI6wjkIT9wox7Vlh605e5VjyqlPI1UdHDpvW2yISxpF0_c8wfLQF5yotw9ETlmwSPyr_nA4BlpUFg7YxyOLOcF8DlB7-egQuUSLHm3FGi18dIIrPFZaIF0YjlZysLNdGxSqHzMMyLzQ1kDh8IDoJD8ylKvw8ElKHg7gs9j620J-hKBI8fdfISMEtU9-U05lNuT9wpP0Z3QcjgeoXiEtqYZN7mkD3DJVzCq4SB3oRWupo5gmrHEq_z7ElYHN4aO4cOJxw_kgFuiNjLqTFTp08C8lUkcsOYB5ZPHUYnmFqGk6XARe_9KJkjLV5I"
VALID_NON_ADMIN_ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzZXNzaW9uSWQiOiJ0ZXN0IiwidXNlcm5hbWUiOiJ0ZXN0IG5hbWUiLCJ1c2VySXNBZG1pbiI6ZmFsc2UsImV4cCI6OTk5OTk5OTk5OX0.ZrvLcWueXfix-dOtuFWdpZuUZAM8WrhtqUffEfZhLJPDbCe-I_D3Bcikznhtkb1k8-Kcj9MiLdUcaFXT-SvyYpc_c2Zj690FMVqfrR9yjaGGWG-2Lx2izedjSFoNu7zT779hmDanzTFNtLzSZeSU8GhXXSsrzgY2FwcDMNHiCcKb6JlcsrmSRIKQCiKK4k_VadJ7e7EioCN9tVAGiORwOy81r1m5RqSui6y8SvYzTFXSbDwjTErTVUfdIsUcN9_i_WEMn1sPztVPeQ_0o3sW0XsIxK-peuiqAqnX67OQpNQtUoMd_RtY603U9zdGujCDW-zYz-vIzWhUu5GNyFaA_1zJIuS-Ga3gGS-QXrLTYrosBTCpK0OCZp8mM4Guue7obKa5zeEL-Cq2-WlrLuPMlxCPrPH1qu_pMtYO-yaMIrfX6Xt7g-0p2ZQVIaR-vesXJC6MTIO-bqq8rIv7ToImf774gY2Fg5EiNnhkJAml8AaKfSynWsRoV7YsXoCnlqGLCwE4-RyRoq-rmm4ms1zEzwl38ydPWUzNqQMTkwqj5eYsRw-ncfVssnP0VcZ5HCcHIXKHOVuHrxqc5wJg-MkhCfJazOb8pjyDZg6fW4Omsr54Rthz3R7jeska0AbinZzAlPJSwdx9ouPxvdAD2hWxAPnp9Ii16gn50V38eMLm3wA"
INVALID_ACCESS_TOKEN = VALID_ACCESS_TOKEN + '1'
EXPIRED_ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzZXNzaW9uSWQiOiJ0ZXN0IiwidXNlcm5hbWUiOiJ0ZXN0IG5hbWUiLCJ1c2VySXNBZG1pbiI6ZmFsc2UsImV4cCI6MTU3ODQ0MTU5OX0.cZh9eezkKpuUhx49NQORXm9Nq6VaMNA9hI_XtRlwr9wO2RkX6g4DE0I9ls9QDp8mNs1ZrKolM1aAa-3xi6GiHQBK9hQFSVZK8UYd_wG4AbnuBUmWypSKB3AD_fUtNeCv1NxOdKQPbx6CgKguWN3DmjAFrc84nrrX-FHGx5IsmiD_TeSudqBHiG7Kqbn4FWhVmyzcwTs4d0eCtTpJNGaLcNNp5WuR8GX0CnCZdgM6eFM8pvoAZGJ_lXEQ3ayCY-4CShWinAa2G1x_mwgd0-y5KhmjU1DdY6G0qqlmeFBO4Qz6LSoEjp5KHiSTSRNLVr9FIHYJY5v2MhZ9Jt-bp3e7mDEyR8M8RtnVRGAtn_KKovh0e5v2AgFnUsOVYtj3g_gr5lbiwpVY9cNa24HJqPxSb9WnjBLWYHcyhLCZKDTtZ0xdCDeQrO772rCpfb2tSif6LijQJRuhJzvjdcHJgZNeFDoF0bGha_brqRqOo4ayIn-BrfuBmN4ShplLs_Q_vGg76do7Px1QVc4_1mrXgIdl9xDCtv-z80E7Y6LzEPtEGwfoyqLJWhyF5HRYIUgJSakK6ZtZsFGMIC3uCCMZGD5KZDUcc_UKZOIZZ9mlDXyPkIehZ1AoQszZKJbkvoDf9xYLQLpdf7-0vIIhqqaIM2VjOmKD-BQjUvrfyd-Olv_sPAw"
ACCESS_TOKEN_WITHOUT_ADMIN_INFO = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzZXNzaW9uSWQiOiJ0ZXN0IiwidXNlcm5hbWUiOiJ0ZXN0IG5hbWUiLCJleHAiOjk5OTk5OTk5OTl9.beDpd6SrucSThtzszb1sfr4xieVpWzoZ7uVRj6vOeIy-MI0yAfn7M-PnDOdZoyOMJbGEP_BWNo3e4zpiyv9wxx-TVL_EKccdre92seYPFI8pOnAm0OlmbM9hOwSSQuhAuqSAzxSupU0V2CPXN9YG_xOFFhrpAgNIltyqcpkv0VArxYbniJtGEJt_WTwn15XO1oEDK7-3w7CNidQ2_BUrp0ZfYDVjgJXpaK6-op_7KLUBqXzZtAIbf2Z97O05sZk5Iv0citk9Mqh3a17CUajNDJAQAwBuUomwIvqm0flB3SriEfrUx7tteNlH8ziZ1Vs3b9Dg6hjvF0jDkC8BL2LZoI6eYP7iVIyS-ZwGEjnE9qiBqblP9E4ENVygCfP7A1SDG8XsCmkIt1lXFKM8qgjfPaompOI8rY5mJEwgbZTJmDCPpzJ9ethJmpuZbuDOQYjI1occkIeeOkzJsHnm3vkv4TTZPgifckUlIJdXaDFGGLZYC05cMFB2x-DdOQuzX1Dvr4OAKQH_g5vEibXhH3amMqRBNlHZlmc0WundBmo5hJFSUvR7oWa0nprWk1iPUlMuijyedTyVk51tJqVe1orDg2W2yp7ehdgAWJiWAwOpYL4Tbj-rypOq12tqnemaS5eykG0Ybo7fNG_4hTbTiX4SsPIhEusVte7-y-vpNVbwefE"


@mock.patch("src.admin.PUBLIC_KEY", PUBLIC_KEY)
@mock.patch("src.admin.MAINTENANCE_CONFIG_PATH", MAINTENANCE_CONFIG_PATH)
class TestMaintenanceMode(TestCase):
    def setUp(self):
        self.maintenance_mode = MaintenanceMode()

    @mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(MAINTENANCE_STATE)))
    def test_get_state(self):
        assert self.maintenance_mode.get_state() == MAINTENANCE_STATE

    def test_set_state_valid_token(self):
        mock_json_dump = mock.patch.object(admin.json, "dump").start()
        with mock.patch("builtins.open", mock.mock_open()) as mocked_file:
            result = self.maintenance_mode.set_state(VALID_ACCESS_TOKEN, MAINTENANCE_STATE)

        mocked_file.assert_called_once_with(MAINTENANCE_CONFIG_PATH, 'w')
        mock_json_dump.assert_called_once_with(MAINTENANCE_STATE,
                                               mocked_file.return_value)
        self.assertEqual(result, ("Maintenance mode state successfully updated", 200))

    def test_set_state_invalid_token(self):
        result = self.maintenance_mode.set_state(INVALID_ACCESS_TOKEN, MAINTENANCE_STATE)
        self.assertEqual(result, ("Access token was not valid", 403))

    def test_set_state_expired_token(self):
        result = self.maintenance_mode.set_state(EXPIRED_ACCESS_TOKEN, MAINTENANCE_STATE)
        self.assertEqual(result, ("Access token was not valid", 403))

    @mock.patch("src.admin.BLACKLIST", [VALID_ACCESS_TOKEN])
    def test_set_state_blacklisted_token(self):
        result = self.maintenance_mode.set_state(VALID_ACCESS_TOKEN, MAINTENANCE_STATE)
        self.assertEqual(result, ("Access token was not valid", 403))

    def test_set_state_valid_non_admin_token(self):
        result = self.maintenance_mode.set_state(VALID_NON_ADMIN_ACCESS_TOKEN,
                                                 MAINTENANCE_STATE)
        self.assertEqual(result, ("Unauthorized", 403))

    def test_set_state_token_without_admin_info(self):
        result = self.maintenance_mode.set_state(ACCESS_TOKEN_WITHOUT_ADMIN_INFO,
                                                 MAINTENANCE_CONFIG_PATH)
        self.assertEqual(result, ("Unauthorized", 403))

    def test_set_state_file_update_failure(self):
        with mock.patch("builtins.open", mock.mock_open()) as mocked_file:
            mocked_file.side_effect = IOError()
            result = self.maintenance_mode.set_state(VALID_ACCESS_TOKEN, MAINTENANCE_STATE)
        self.assertEqual(result, ("Failed to update maintenance mode state", 500))
