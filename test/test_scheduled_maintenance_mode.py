import json
from unittest import TestCase, mock

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
