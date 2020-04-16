from common.config import config

with open(config.get_private_key_path(), "r") as f:
    PRIVATE_KEY = f.read()

with open(config.get_public_key_path(), "r") as f:
    PUBLIC_KEY = f.read()

ICAT_URL = config.get_icat_url()
ACCESS_TOKEN_VALID_FOR = config.get_access_token_valid_for()
REFRESH_TOKEN_VALID_FOR = config.get_refresh_token_valid_for()
BLACKLIST = config.get_blacklist()
SECURE = True
VERIFY = config.get_verify()
