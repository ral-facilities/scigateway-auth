from scigateway_auth.common.config import config

try:
    with open(config.get_private_key_path(), "r") as f:
        PRIVATE_KEY = f.read()
except FileNotFoundError:
    PRIVATE_KEY = ""

try:
    with open(config.get_public_key_path(), "r") as f:
        PUBLIC_KEY = f.read()
except FileNotFoundError:
    PUBLIC_KEY = ""

ICAT_URL = config.get_icat_url()
ACCESS_TOKEN_VALID_FOR = config.get_access_token_valid_for()
REFRESH_TOKEN_VALID_FOR = config.get_refresh_token_valid_for()
BLACKLIST = config.get_blacklist()
ADMIN_USERS = config.get_admin_users()
MAINTENANCE_CONFIG_PATH = config.get_maintenance_config_path()
SCHEDULED_MAINTENANCE_CONFIG_PATH = config.get_scheduled_maintenance_config_path()
SECURE = True
VERIFY = config.get_verify()
