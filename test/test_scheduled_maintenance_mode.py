import json
from unittest import TestCase, mock

from src import admin
from src.admin import ScheduledMaintenanceMode

with open("test/keys/jwt-key.pub", "r") as f:
    PUBLIC_KEY = f.read()

SCHEDULED_MAINTENANCE_STATE = "path/to/config/test_config.json"
SCHEDULED_MAINTENANCE_CONFIG_PATH = {"test": "test"}


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
            result = self.scheduled_maintenance_mode.set_state(SCHEDULED_MAINTENANCE_STATE)

        mocked_file.assert_called_once_with(SCHEDULED_MAINTENANCE_CONFIG_PATH, 'w')
        mock_json_dump.assert_called_once_with(SCHEDULED_MAINTENANCE_STATE,
                                               mocked_file.return_value)
        self.assertEqual(result, ("Scheduled maintenance mode state successfully updated", 200))

    def test_set_state_file_update_failure(self):
        with mock.patch("builtins.open", mock.mock_open()) as mocked_file:
            mocked_file.side_effect = IOError()
            result = self.scheduled_maintenance_mode.set_state(SCHEDULED_MAINTENANCE_STATE)
        self.assertEqual(result, ("Failed to update scheduled maintenance mode state", 500))