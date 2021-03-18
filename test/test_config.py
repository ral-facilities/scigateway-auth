import json
from unittest import mock, TestCase

from scigateway_auth.common.config import _load_config, Config, get_config_value

CONFIG_VALUES = {"verify": True}


@mock.patch(
    "builtins.open",
    mock.mock_open(read_data=json.dumps(CONFIG_VALUES)),
)
class TestConfig(TestCase):
    def test__load_config(self):
        self.assertEqual(_load_config(), CONFIG_VALUES)

    def test__load_config_failure(self):
        with mock.patch("builtins.open", mock.mock_open()) as mocked_file:
            mocked_file.side_effect = IOError()
            with self.assertRaises(SystemExit):
                _load_config()

    def test_get_config_value(self):
        self.assertEqual(get_config_value(Config.VERIFY), True)

    def test_get_config_value_missing(self):
        with self.assertRaises(SystemExit):
            get_config_value(Config.BLACKLIST)
