# app/logger.py

import logging
from colorlog import ColoredFormatter

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler()
         # Format only LEVELNAME with color
        formatter = ColoredFormatter(
            fmt="%(name)s - %(log_color)s%(levelname)-8s%(reset)s: %(message)s",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
            reset=True,
            style="%"  # Use %-style formatting
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
