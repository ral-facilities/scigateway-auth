import logging.config

from scigateway_auth.common.config import Config, get_config_value

logger_config = {
    "version": 1,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] {%(module)s:%(filename)s:%(funcName)s:"
            "%(lineno)d} %(levelname)s - %(message)s  ",
        },
    },
    "handlers": {
        "default": {
            "level": get_config_value(Config.LOG_LEVEL),
            "formatter": "default",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": get_config_value(Config.LOG_LOCATION),
            "maxBytes": 5000000,
            "backupCount": 10,
        },
    },
    "root": {"level": get_config_value(Config.LOG_LEVEL), "handlers": ["default"]},
}


def setup_logger():
    logging.config.dictConfig(logger_config)
