import logging.config
from pathlib import Path

from scigateway_auth.common.config import config

logger_config = {
    "version": 1,
    "formatters": {"default": {
        "format": "[%(asctime)s] {%(module)s:%(filename)s:%(funcName)s:%(lineno)d} %(levelname)s - %(message)s  ",
    }},
    "handlers": {"default": {
        "level": config.get_log_level(),
        "formatter": "default",
        "class": "logging.handlers.RotatingFileHandler",
        "filename": config.get_log_location(),
        "maxBytes": 5000000,
        "backupCount": 10
    }},
    "root": {
        "level": config.get_log_level(),
        "handlers": ["default"]
    }
}


def setup_logger():
    logging.config.dictConfig(logger_config)
