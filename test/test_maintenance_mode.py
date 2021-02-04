import json
from unittest import TestCase, mock

from src import admin
from src.admin import MaintenanceMode

with open("test/keys/jwt-key.pub", "r") as f:
    PUBLIC_KEY = f.read()
MAINTENANCE_CONFIG_PATH = "path/to/config/test_config.json"
MAINTENANCE_STATE = {"test": "test"}
VALID_ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzZXNzaW9uSWQiOiJ0ZXN0IiwidXNlcm5hbWUiOiJ0ZXN0IG5hbWUiLCJ1c2VySXNBZG1pbiI6dHJ1ZSwiZXhwIjo5OTk5OTk5OTk5fQ.L2pR4ViBiUoZtEYat8boDyfs1RgVbHQS_-MNK7-QfdA4aEzfghJjm53EeySw88zyVpiZcNgO9owu400ywPDmKu0A88i82hhltEd0zIPLd3PfCUUe4NlzZ5aNavuemrQ3FAztc9c0GIJFVBwPkItLmwyL47uTgSBJB_a5y51tVh61g_FLg3Bb7vYwyTyjxIUhrzwc4mXfpeybQae5fcQKJzE3MbZxHEtGYhL9p7ukaaFl1UnGeGba_CALD3kZBLFge50eobiDUx_RTpUHHRrOq4prtiBXZk7LH1xrBIVhEXqJX04aoS-0N7cxtJ5RUcOzLYKNAHo0eBVjIj6cly7aaz_DDEIjDQb51FvvwQBXBN33XOikABrI6wjkIT9wox7Vlh605e5VjyqlPI1UdHDpvW2yISxpF0_c8wfLQF5yotw9ETlmwSPyr_nA4BlpUFg7YxyOLOcF8DlB7-egQuUSLHm3FGi18dIIrPFZaIF0YjlZysLNdGxSqHzMMyLzQ1kDh8IDoJD8ylKvw8ElKHg7gs9j620J-hKBI8fdfISMEtU9-U05lNuT9wpP0Z3QcjgeoXiEtqYZN7mkD3DJVzCq4SB3oRWupo5gmrHEq_z7ElYHN4aO4cOJxw_kgFuiNjLqTFTp08C8lUkcsOYB5ZPHUYnmFqGk6XARe_9KJkjLV5I"
INVALID_ACCESS_TOKEN = VALID_ACCESS_TOKEN + '1'
EXPIRED_ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzZXNzaW9uSWQiOiJ0ZXN0IiwidXNlcm5hbWUiOiJ0ZXN0IG5hbWUiLCJ1c2VySXNBZG1pbiI6ZmFsc2UsImV4cCI6MTU3ODQ0MTU5OX0.cZh9eezkKpuUhx49NQORXm9Nq6VaMNA9hI_XtRlwr9wO2RkX6g4DE0I9ls9QDp8mNs1ZrKolM1aAa-3xi6GiHQBK9hQFSVZK8UYd_wG4AbnuBUmWypSKB3AD_fUtNeCv1NxOdKQPbx6CgKguWN3DmjAFrc84nrrX-FHGx5IsmiD_TeSudqBHiG7Kqbn4FWhVmyzcwTs4d0eCtTpJNGaLcNNp5WuR8GX0CnCZdgM6eFM8pvoAZGJ_lXEQ3ayCY-4CShWinAa2G1x_mwgd0-y5KhmjU1DdY6G0qqlmeFBO4Qz6LSoEjp5KHiSTSRNLVr9FIHYJY5v2MhZ9Jt-bp3e7mDEyR8M8RtnVRGAtn_KKovh0e5v2AgFnUsOVYtj3g_gr5lbiwpVY9cNa24HJqPxSb9WnjBLWYHcyhLCZKDTtZ0xdCDeQrO772rCpfb2tSif6LijQJRuhJzvjdcHJgZNeFDoF0bGha_brqRqOo4ayIn-BrfuBmN4ShplLs_Q_vGg76do7Px1QVc4_1mrXgIdl9xDCtv-z80E7Y6LzEPtEGwfoyqLJWhyF5HRYIUgJSakK6ZtZsFGMIC3uCCMZGD5KZDUcc_UKZOIZZ9mlDXyPkIehZ1AoQszZKJbkvoDf9xYLQLpdf7-0vIIhqqaIM2VjOmKD-BQjUvrfyd-Olv_sPAw"


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

    def test_set_state_file_update_failure(self):
        with mock.patch("builtins.open", mock.mock_open()) as mocked_file:
            mocked_file.side_effect = IOError()
            result = self.maintenance_mode.set_state(VALID_ACCESS_TOKEN, MAINTENANCE_STATE)
        self.assertEqual(result, ("Failed to update maintenance mode state", 500))
