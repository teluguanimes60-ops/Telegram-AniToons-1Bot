"""
config.py

Central configuration for AniToon Bot.

Loads all environment variables, validates required values,
and exposes a Config object for the entire project.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Load .env
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _get_env(
    key: str,
    default: str | None = None,
    required: bool = False,
) -> str:
    value = os.getenv(key, default)

    if required and (value is None or value == ""):
        raise RuntimeError(f"Missing required environment variable: {key}")

    return value


def _get_int(
    key: str,
    default: int,
) -> int:
    try:
        return int(os.getenv(key, default))
    except ValueError as exc:
        raise RuntimeError(f"Environment variable '{key}' must be an integer.") from exc


def _get_bool(
    key: str,
    default: bool = False,
) -> bool:
    value = os.getenv(key)

    if value is None:
        return default

    return value.lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


@dataclass(frozen=True)
class Config:
    # Telegram
    API_ID: int
    API_HASH: str
    BOT_TOKEN: str

    # MongoDB
    MONGO_URI: str
    DATABASE_NAME: str

    # Bot
    BOT_OWNER: int
    BOT_USERNAME: str

    # Server
    HOST: str
    PORT: int

    # Worker
    MAX_ACTIVE_USERS: int
    MAX_CONCURRENT_DOWNLOADS: int
    MAX_CONCURRENT_UPLOADS: int

    # Logging
    LOG_LEVEL: str

    # Paths
    TEMP_PATH: Path
    LOG_PATH: Path
    CACHE_PATH: Path

    # Features
    AUTO_DELETE_TEMP: bool
    AUTO_DELETE_MESSAGES: bool
    FORCE_SUBSCRIBE: bool
    PREMIUM_ENABLED: bool


config = Config(
    API_ID=_get_int("API_ID", 0),
    API_HASH=_get_env("API_HASH", required=True),
    BOT_TOKEN=_get_env("BOT_TOKEN", required=True),

    MONGO_URI=_get_env("MONGO_URI", required=True),
    DATABASE_NAME=_get_env("DATABASE_NAME", "AniToonBot"),

    BOT_OWNER=_get_int("BOT_OWNER", 0),
    BOT_USERNAME=_get_env("BOT_USERNAME", ""),

    HOST=_get_env("HOST", "0.0.0.0"),
    PORT=_get_int("PORT", 10000),

    MAX_ACTIVE_USERS=_get_int("MAX_ACTIVE_USERS", 20),
    MAX_CONCURRENT_DOWNLOADS=_get_int(
        "MAX_CONCURRENT_DOWNLOADS",
        3,
    ),
    MAX_CONCURRENT_UPLOADS=_get_int(
        "MAX_CONCURRENT_UPLOADS",
        3,
    ),

    LOG_LEVEL=_get_env("LOG_LEVEL", "INFO"),

    TEMP_PATH=BASE_DIR / "temp",
    LOG_PATH=BASE_DIR / "logs",
    CACHE_PATH=BASE_DIR / "cache",

    AUTO_DELETE_TEMP=_get_bool("AUTO_DELETE_TEMP", True),
    AUTO_DELETE_MESSAGES=_get_bool(
        "AUTO_DELETE_MESSAGES",
        True,
    ),
    FORCE_SUBSCRIBE=_get_bool("FORCE_SUBSCRIBE", False),
    PREMIUM_ENABLED=_get_bool("PREMIUM_ENABLED", True),
)

# Automatically create required directories
config.TEMP_PATH.mkdir(parents=True, exist_ok=True)
config.LOG_PATH.mkdir(parents=True, exist_ok=True)
config.CACHE_PATH.mkdir(parents=True, exist_ok=True)
