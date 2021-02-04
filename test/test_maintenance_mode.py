import json
from unittest import TestCase, mock

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
