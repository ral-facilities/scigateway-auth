import json
from unittest import TestCase, mock

from src import admin
from src.admin import MaintenanceMode
from test.testutils import PUBLIC_KEY, MAINTENANCE_CONFIG_PATH, MAINTENANCE_STATE, \
    VALID_ACCESS_TOKEN, INVALID_ACCESS_TOKEN, EXPIRED_ACCESS_TOKEN, VALID_NON_ADMIN_ACCESS_TOKEN, \
    ACCESS_TOKEN_WITHOUT_ADMIN_INFO


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
