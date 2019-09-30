import json
import sys
from pathlib import Path


class Config(object):

    def __init__(self):
        with open(Path("config.json")) as target:
            self.config = json.load()
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


config = Config()
