"""
logger.py

Production-ready logging configuration for AniToon Bot.
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from config import config

LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | "
    "%(filename)s:%(lineno)d | %(message)s"
)

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def _create_formatter() -> logging.Formatter:
    return logging.Formatter(
        fmt=LOG_FORMAT,
        datefmt=DATE_FORMAT,
    )


def _create_file_handler(
    file_path: Path,
    level: int,
) -> RotatingFileHandler:
    handler = RotatingFileHandler(
        filename=file_path,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8",
    )
    handler.setLevel(level)
    handler.setFormatter(_create_formatter())
    return handler


def _create_console_handler(level: int) -> logging.StreamHandler:
    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(_create_formatter())
    return handler


def setup_logger() -> None:
    """
    Configure the root logger.
    """

    level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)

    root_logger = logging.getLogger()

    if root_logger.handlers:
        return

    root_logger.setLevel(level)

    root_logger.addHandler(
        _create_console_handler(level)
    )

    root_logger.addHandler(
        _create_file_handler(
            config.LOG_PATH / "bot.log",
            level,
        )
    )

    root_logger.addHandler(
        _create_file_handler(
            config.LOG_PATH / "errors.log",
            logging.ERROR,
        )
    )

    logging.getLogger("pyrogram").setLevel(logging.WARNING)
    logging.getLogger("motor").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Return a configured logger instance.
    """

    setup_logger()
    return logging.getLogger(name)
