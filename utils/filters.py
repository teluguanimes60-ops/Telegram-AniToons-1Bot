"""
utils/filters.py

Custom Pyrogram filters for AniToons Bot.
"""

from __future__ import annotations

from pyrogram import filters
from pyrogram.types import Message

from config import Config


# --------------------------------------------------
# Owner Filter
# --------------------------------------------------

def _is_owner(_, __, message: Message) -> bool:
    return (
        message.from_user is not None
        and message.from_user.id == Config.OWNER_ID
    )


owner = filters.create(_is_owner)


# --------------------------------------------------
# Admin Filter
# --------------------------------------------------

def _is_admin(_, __, message: Message) -> bool:
    return (
        message.from_user is not None
        and message.from_user.id in Config.ADMIN_IDS
    )


admin = filters.create(_is_admin)


# --------------------------------------------------
# Private Chat
# --------------------------------------------------

private = filters.private


# --------------------------------------------------
# Group Chat
# --------------------------------------------------

group = filters.group


# --------------------------------------------------
# Media Filter
# --------------------------------------------------

media = (
    filters.document
    | filters.video
    | filters.audio
    | filters.photo
    | filters.animation
    | filters.voice
    | filters.video_note
)


# --------------------------------------------------
# URL Filter
# --------------------------------------------------

url = filters.regex(
    r"^(https?://|www\.)"
)


# --------------------------------------------------
# Archive Files
# --------------------------------------------------

archive = filters.regex(
    r".*\.(zip|rar|7z|tar|gz)$"
)


# --------------------------------------------------
# APK Files
# --------------------------------------------------

apk = filters.regex(
    r".*\.apk$"
)


# --------------------------------------------------
# PDF Files
# --------------------------------------------------

pdf = filters.regex(
    r".*\.pdf$"
)


# --------------------------------------------------
# Image Files
# --------------------------------------------------

image = (
    filters.photo
    | filters.regex(
        r".*\.(jpg|jpeg|png|webp)$"
    )
)


# --------------------------------------------------
# Video Files
# --------------------------------------------------

video = filters.video


# --------------------------------------------------
# Audio Files
# --------------------------------------------------

audio = filters.audio


# --------------------------------------------------
# Document Files
# --------------------------------------------------

document = filters.document


# --------------------------------------------------
# Callback Query
# --------------------------------------------------

callback = filters.regex(".*")


# --------------------------------------------------
# Text Messages
# --------------------------------------------------

text = filters.text & ~filters.command(
    [
        "start",
        "help",
    ]
)


# --------------------------------------------------
# Commands
# --------------------------------------------------

start = filters.command("start")

help_cmd = filters.command("help")

settings = filters.command("settings")

admin_cmd = filters.command("admin")

broadcast = filters.command("broadcast")

stats = filters.command("stats")
