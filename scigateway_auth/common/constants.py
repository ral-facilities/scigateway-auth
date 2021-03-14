from scigateway_auth.common.config import Config, get_config_value

try:
    with open(get_config_value(Config.PRIVATE_KEY_PATH), "r") as f:
        PRIVATE_KEY = f.read()
except FileNotFoundError:
    PRIVATE_KEY = ""

try:
    with open(get_config_value(Config.PUBLIC_KEY_PATH), "r") as f:
        PUBLIC_KEY = f.read()
except FileNotFoundError:
    PUBLIC_KEY = ""

ICAT_URL = get_config_value(Config.ICAT_URL)
ACCESS_TOKEN_VALID_FOR = get_config_value(Config.ACCESS_TOKEN_VALID_FOR)
REFRESH_TOKEN_VALID_FOR = get_config_value(Config.REFRESH_TOKEN_VALID_FOR)
BLACKLIST = get_config_value(Config.BLACKLIST)
ADMIN_USERS = get_config_value(Config.ADMIN_USERS)
MAINTENANCE_CONFIG_PATH = get_config_value(Config.MAINTENANCE_CONFIG_PATH)
SCHEDULED_MAINTENANCE_CONFIG_PATH = get_config_value(
    Config.SCHEDULED_MAINTENANCE_CONFIG_PATH,
)
SECURE = True
VERIFY = get_config_value(Config.VERIFY)
