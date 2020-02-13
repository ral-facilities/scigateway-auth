from common.config import config

SECRET = "shh"
ICAT_URL = config.get_icat_url()
ACCESS_TOKEN_VALID_FOR = config.get_access_token_valid_for()
REFRESH_TOKEN_VALID_FOR = config.get_refresh_token_valid_for()
BLACKLIST = config.get_blacklist()
SECURE = True
