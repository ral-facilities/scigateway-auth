from common.config import config

with open(config.get_private_key_path(), "r") as f:
    PRIVATE_KEY = f.read()

with open(config.get_public_key_path(), "r") as f:
    PUBLIC_KEY = f.read()

ICAT_AUTH_URL = config.get_icat_auth_url()
