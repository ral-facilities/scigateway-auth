import json
from unittest import TestCase, mock

from src import admin
from src.admin import MaintenanceMode

with open("test/keys/jwt-key.pub", "r") as f:
    PUBLIC_KEY = f.read()
MAINTENANCE_CONFIG_PATH = "path/to/config/test_config.json"
MAINTENANCE_STATE = {"test": "test"}


@mock.patch("src.admin.PUBLIC_KEY", PUBLIC_KEY)
@mock.patch("src.admin.MAINTENANCE_CONFIG_PATH", MAINTENANCE_CONFIG_PATH)
class TestMaintenanceMode(TestCase):
    def setUp(self):
        self.maintenance_mode = MaintenanceMode()

    @mock.patch("builtins.open", mock.mock_open(read_data=json.dumps(MAINTENANCE_STATE)))
    def test_get_state(self):
        assert self.maintenance_mode.get_state() == MAINTENANCE_STATE

    def test_set_state(self):
        mock_json_dump = mock.patch.object(admin.json, "dump").start()
        with mock.patch("builtins.open", mock.mock_open()) as mocked_file:
            result = self.maintenance_mode.set_state(MAINTENANCE_STATE)

        mocked_file.assert_called_once_with(MAINTENANCE_CONFIG_PATH, 'w')
        mock_json_dump.assert_called_once_with(MAINTENANCE_STATE,
                                               mocked_file.return_value)
        self.assertEqual(result, ("Maintenance mode state successfully updated", 200))

    def test_set_state_file_update_failure(self):
        with mock.patch("builtins.open", mock.mock_open()) as mocked_file:
            mocked_file.side_effect = IOError()
            result = self.maintenance_mode.set_state(MAINTENANCE_STATE)
        self.assertEqual(result, ("Failed to update maintenance mode state", 500))
