from enum import Enum
import json
from pathlib import Path
import sys


class Config(Enum):
    HOST = "host"
    PORT = "port"
    DEBUG_MODE = "debug_mode"
    ICAT_URL = "icat_url"
    LOG_LEVEL = "log_level"
    LOG_LOCATION = "log_location"
    PRIVATE_KEY_PATH = "private_key_path"
    PUBLIC_KEY_PATH = "public_key_path"
    ACCESS_TOKEN_VALID_FOR = "access_token_valid_for"  # noqa: S105
    REFRESH_TOKEN_VALID_FOR = "refresh_token_valid_for"  # noqa: S105
    BLACKLIST = "blacklist"
    ADMIN_USERS = "admin_users"
    MAINTENANCE_CONFIG_PATH = "maintenance_config_path"
    SCHEDULED_MAINTENANCE_CONFIG_PATH = "scheduled_maintenance_config_path"
    VERIFY = "verify"


def _load_config():
    """
    Loads config values from the JSON config file. Exits the application if it
    fails to locate/ read the contents of the file.
    :return: config values in form of a dictionary
    """
    try:
        with open(Path(__file__).parent.parent / "config.json") as target:
            return json.load(target)
    except IOError:
        sys.exit("Error loading config file")


def get_config_value(config):
    """
    Given a Config enum, it returns a config value. Reloads the values from the
    config file so that a restart of the application is not required for config
    changes to take effect. Exits the application if the provided enum is not in
    the config dictionary.
    :return: config value
    """
    config_values = _load_config()
    try:
        return config_values[config.value]
    except KeyError:
        sys.exit("Missing config value, %s" % config.value)
