import json
import sys
from pathlib import Path


class Config(object):

    def __init__(self):
        with open(Path(__file__).parent.parent.parent / "config.json") as target:
            self.config = json.load(target)
        target.close()

    def get_host(self):
        try:
            return self.config["host"]
        except:
            sys.exit("Missing config value: host")

    def get_port(self):
        try:
            return self.config["port"]
        except:
            sys.exit("Missing config value: port")

    def is_debug_mode(self):
        try:
            return self.config["debug_mode"]
        except:
            sys.exit("Missing config value: debug_mode")

    def get_icat_url(self):
        try:
            return self.config["icat_url"]
        except:
            sys.exit("Missing config value: icat_url")

    def get_log_level(self):
        try:
            return self.config["log_level"]
        except:
            sys.exit("Missing config value, log_level")

    def get_access_token_valid_for(self):
        try:
            return self.config["access_token_valid_for"]
        except:
            sys.exit("Missing config value, access_token_valid_for")

    def get_refresh_token_valid_for(self):
        try:
            return self.config["refresh_token_valid_for"]
        except:
            sys.exit("Missing config value, refresh_token_valid_for")

    def get_blacklist(self):
        try:
            return self.config["blacklist"]
        except:
            sys.exit("Missing config value, blacklist")


config = Config()
