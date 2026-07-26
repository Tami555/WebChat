import logging.config
from pathlib import Path

from src.core.config import settings


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": settings.logging.format,
            "datefmt": settings.logging.datefmt,
        },
        "colored": {
            "()": "src.utils.logging.formatters.ColorFormatter",
            "format": settings.logging.format,
            "datefmt": settings.logging.datefmt,
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": settings.logging.level,
            "formatter": "colored",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.FileHandler",
            "level": "WARNING",
            "formatter": "default",
            "filename": "./logs/app.log",
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "src": {  
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "sqlalchemy": {
            "handlers": [],
            "level": "WARNING",
            "propagate": False,
        },
        "": {  # Root logger
            "handlers": ["file"],
            "level": "ERROR",
        },
    },
}


def setup_logging():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logging.config.dictConfig(LOGGING_CONFIG)
