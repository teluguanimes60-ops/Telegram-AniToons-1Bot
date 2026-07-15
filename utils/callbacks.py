"""
utils/callbacks.py

Central callback data constants.
"""

from __future__ import annotations

from enum import StrEnum


class Callback(StrEnum):
    # Navigation
    HOME = "home"
    BACK = "back"
    CLOSE = "close"

    # Main Menu
    HELP = "help"
    ABOUT = "about"
    SETTINGS = "settings"

    # File Actions
    RENAME = "rename"
    RENAME_MENU = "rename_menu"

    CONVERT = "convert"
    CONVERT_MENU = "convert_menu"

    CAPTION = "caption"
    THUMBNAIL = "thumbnail"

    # Thumbnail
    THUMB_UPLOAD = "thumb_upload"
    THUMB_AUTO = "thumb_auto"
    THUMB_REMOVE = "thumb_remove"
    THUMB_PREVIEW = "thumb_preview"

    # Queue
    QUEUE_INFO = "queue_info"
    QUEUE_CANCEL = "queue_cancel"

    # Progress
    PAUSE = "pause"
    RESUME = "resume"
    CANCEL = "cancel"

    # Force Subscribe
    FSUB_REFRESH = "fsub_refresh"
    FSUB_CONTINUE = "fsub_continue"

    # Premium
    PREMIUM = "premium"
    PREMIUM_BUY = "premium_buy"
    PREMIUM_STATUS = "premium_status"

    # Admin
    ADMIN = "admin"
    ADMIN_STATS = "admin_stats"
    ADMIN_USERS = "admin_users"
    ADMIN_PREMIUM = "admin_premium"
    ADMIN_CHANNELS = "admin_channels"
    ADMIN_QUEUE = "admin_queue"
    ADMIN_BROADCAST = "admin_broadcast"
    ADMIN_SETTINGS = "admin_settings"
    ADMIN_LOGS = "admin_logs"
    ADMIN_RESTART = "admin_restart"
    ADMIN_SHUTDOWN = "admin_shutdown"

    # Broadcast
    BROADCAST_TEXT = "broadcast_text"
    BROADCAST_PHOTO = "broadcast_photo"
    BROADCAST_VIDEO = "broadcast_video"
    BROADCAST_DOCUMENT = "broadcast_document"

    # Generic
    IGNORE = "ignore"


class Prefix(StrEnum):
    QUALITY = "quality"
    FORMAT = "format"
    COMPRESS = "compress"
    PAGE = "page"
    SEARCH = "search"
    LANGUAGE = "language"
    THEME = "theme"


def quality(value: int) -> str:
    return f"{Prefix.QUALITY}:{value}"


def format_(name: str) -> str:
    return f"{Prefix.FORMAT}:{name.lower()}"


def compress(level: str) -> str:
    return f"{Prefix.COMPRESS}:{level.lower()}"


def page(prefix: str, number: int) -> str:
    return f"{prefix}:{number}"


def is_quality(data: str) -> bool:
    return data.startswith(f"{Prefix.QUALITY}:")


def is_format(data: str) -> bool:
    return data.startswith(f"{Prefix.FORMAT}:")


def is_compress(data: str) -> bool:
    return data.startswith(f"{Prefix.COMPRESS}:")


def get_value(data: str) -> str:
    if ":" not in data:
        return data

    return data.split(":", 1)[1]
