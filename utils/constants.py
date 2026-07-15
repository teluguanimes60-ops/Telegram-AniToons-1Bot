"""
utils/constants.py

Global constants for AniToons Bot.
"""

from __future__ import annotations

from pathlib import Path

# --------------------------------------------------
# Directories
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

TEMP_DIR = BASE_DIR / "temp"
CACHE_DIR = BASE_DIR / "cache"
LOG_DIR = BASE_DIR / "logs"

TEMP_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# Progress
# --------------------------------------------------

PROGRESS_UPDATE_INTERVAL = 2

PROGRESS_BAR_LENGTH = 20

# --------------------------------------------------
# Queue
# --------------------------------------------------

MAX_ACTIVE_JOBS = 20

QUEUE_CHECK_INTERVAL = 1

# --------------------------------------------------
# Telegram
# --------------------------------------------------

MAX_FILENAME_LENGTH = 255

DEFAULT_PARSE_MODE = "markdown"

# --------------------------------------------------
# Thumbnail
# --------------------------------------------------

THUMBNAIL_WIDTH = 320
THUMBNAIL_HEIGHT = 320

# --------------------------------------------------
# FFmpeg
# --------------------------------------------------

SUPPORTED_VIDEO_FORMATS = (
    "mp4",
    "mkv",
    "avi",
    "mov",
    "webm",
    "ts",
)

SUPPORTED_AUDIO_FORMATS = (
    "mp3",
    "aac",
    "flac",
    "ogg",
    "wav",
)

SUPPORTED_IMAGE_FORMATS = (
    "jpg",
    "jpeg",
    "png",
    "webp",
)

QUALITY_LEVELS = (
    2160,
    1440,
    1080,
    720,
    480,
    360,
    240,
    144,
)

COMPRESSION_LEVELS = (
    "low",
    "medium",
    "high",
    "extreme",
)

# --------------------------------------------------
# Cleanup
# --------------------------------------------------

TEMP_FILE_EXPIRY = 60 * 60

AUTO_DELETE_SECONDS = 300

# --------------------------------------------------
# Broadcast
# --------------------------------------------------

BROADCAST_BATCH_SIZE = 25

BROADCAST_DELAY = 0.1

# --------------------------------------------------
# Premium
# --------------------------------------------------

FREE_QUEUE_LIMIT = 1

PREMIUM_QUEUE_LIMIT = 999999

# --------------------------------------------------
# Force Subscribe
# --------------------------------------------------

MAX_FORCE_SUB_CHANNELS = 20

# --------------------------------------------------
# Default Caption Variables
# --------------------------------------------------

CAPTION_VARIABLES = (
    "{filename}",
    "{size}",
    "{quality}",
    "{duration}",
    "{username}",
    "{date}",
)

# --------------------------------------------------
# Default Emojis
# --------------------------------------------------

EMOJI_SUCCESS = "✅"
EMOJI_ERROR = "❌"
EMOJI_WARNING = "⚠️"
EMOJI_LOADING = "⏳"
EMOJI_DOWNLOAD = "📥"
EMOJI_UPLOAD = "📤"
EMOJI_PROCESS = "⚙️"

# --------------------------------------------------
# Version
# --------------------------------------------------

BOT_NAME = "AniToons Bot"

VERSION = "1.0.0"
