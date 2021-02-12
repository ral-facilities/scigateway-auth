import json
from unittest import TestCase, mock

from src import admin
from src.admin import ScheduledMaintenanceMode
from test.testutils import PUBLIC_KEY, MAINTENANCE_STATE, MAINTENANCE_CONFIG_PATH, \
    VALID_ACCESS_TOKEN, INVALID_ACCESS_TOKEN, EXPIRED_ACCESS_TOKEN, VALID_NON_ADMIN_ACCESS_TOKEN, \
    ACCESS_TOKEN_WITHOUT_ADMIN_INFO

SCHEDULED_MAINTENANCE_STATE = MAINTENANCE_STATE
SCHEDULED_MAINTENANCE_CONFIG_PATH = MAINTENANCE_CONFIG_PATH


@mock.patch("src.admin.PUBLIC_KEY", PUBLIC_KEY)
@mock.patch("src.admin.SCHEDULED_MAINTENANCE_CONFIG_PATH", SCHEDULED_MAINTENANCE_CONFIG_PATH)
class TestScheduledMaintenanceMode(TestCase):
    def setUp(self):
        self.scheduled_maintenance_mode = ScheduledMaintenanceMode()

    @mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(SCHEDULED_MAINTENANCE_STATE)))
    def test_get_state(self):
        assert self.scheduled_maintenance_mode.get_state() == SCHEDULED_MAINTENANCE_STATE

    def test_set_state_valid_token(self):
        mock_json_dump = mock.patch.object(admin.json, "dump").start()
        with mock.patch("builtins.open", mock.mock_open()) as mocked_file:
            result = self.scheduled_maintenance_mode.set_state(VALID_ACCESS_TOKEN,
                                                               SCHEDULED_MAINTENANCE_STATE)

        mocked_file.assert_called_once_with(SCHEDULED_MAINTENANCE_CONFIG_PATH, 'w')
        mock_json_dump.assert_called_once_with(SCHEDULED_MAINTENANCE_STATE,
                                               mocked_file.return_value)
        self.assertEqual(result, ("Scheduled maintenance mode state successfully updated", 200))

    def test_set_state_invalid_token(self):
        result = self.scheduled_maintenance_mode.set_state(INVALID_ACCESS_TOKEN,
                                                           SCHEDULED_MAINTENANCE_STATE)
        self.assertEqual(result, ("Access token was not valid", 403))

    def test_set_state_expired_token(self):
        result = self.scheduled_maintenance_mode.set_state(EXPIRED_ACCESS_TOKEN,
                                                           SCHEDULED_MAINTENANCE_STATE)
        self.assertEqual(result, ("Access token was not valid", 403))

    @mock.patch("src.admin.BLACKLIST", [VALID_ACCESS_TOKEN])
    def test_set_state_blacklisted_token(self):
        result = self.scheduled_maintenance_mode.set_state(VALID_ACCESS_TOKEN,
                                                           SCHEDULED_MAINTENANCE_STATE)
        self.assertEqual(result, ("Access token was not valid", 403))

    def test_set_state_valid_non_admin_token(self):
        result = self.scheduled_maintenance_mode.set_state(VALID_NON_ADMIN_ACCESS_TOKEN,
                                                           SCHEDULED_MAINTENANCE_STATE)
        self.assertEqual(result, ("Unauthorized", 403))

    def test_set_state_token_without_admin_info(self):
        result = self.scheduled_maintenance_mode.set_state(ACCESS_TOKEN_WITHOUT_ADMIN_INFO,
                                                           SCHEDULED_MAINTENANCE_CONFIG_PATH)
        self.assertEqual(result, ("Unauthorized", 403))

    def test_set_state_file_update_failure(self):
        with mock.patch("builtins.open", mock.mock_open()) as mocked_file:
            mocked_file.side_effect = IOError()
            result = self.scheduled_maintenance_mode.set_state(VALID_ACCESS_TOKEN,
                                                               SCHEDULED_MAINTENANCE_STATE)
        self.assertEqual(result, ("Failed to update scheduled maintenance mode state", 500))
