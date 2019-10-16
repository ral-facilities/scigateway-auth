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

    def get_icat_auth_url(self):
        try:
            return self.config["icat_auth_url"]
        except:
            sys.exit("Missing config value: icat_auth_url")


config = Config()
