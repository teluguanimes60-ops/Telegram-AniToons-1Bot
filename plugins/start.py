"""
plugins/start.py

Start command and basic menu handlers.
"""

from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    CallbackQuery,
)

from database.users import add_user
from utils.keyboards import keyboards


START_TEXT = """
<b>Welcome to AniToons Bot</b> 🎬

Your all-in-one Telegram media assistant.

Features:

• Rename files
• Convert videos
• Compress media
• Add thumbnails
• Extract audio
• Fast processing
• Queue system

Choose an option below 👇
"""


HELP_TEXT = """
<b>Help Menu</b> ❓

Send me any Telegram file:

Supported:
• Video
• Document
• Audio
• Photo
• ZIP
• APK
• PDF

Available actions:

✏ Rename
🎬 Convert
🗜 Compress
🖼 Thumbnail
📝 Caption

Use the buttons to continue.
"""


ABOUT_TEXT = """
<b>About AniToons Bot</b> ℹ️

A powerful Telegram media processing bot.

Built with:

• Pyrogram
• MongoDB
• FFmpeg
• AsyncIO

Fast, modular and scalable.
"""


# --------------------------------------------------
# Start Command
# --------------------------------------------------


@Client.on_message(
    filters.command("start")
    & filters.private
)
async def start_command(
    client: Client,
    message: Message,
):

    user = message.from_user

    if user:

        await add_user(
            user.id,
            user.first_name,
        )

    await message.reply_text(
        START_TEXT,
        reply_markup=keyboards.start(),
    )


# --------------------------------------------------
# Help Command
# --------------------------------------------------


@Client.on_message(
    filters.command("help")
    & filters.private
)
async def help_command(
    client: Client,
    message: Message,
):

    await message.reply_text(
        HELP_TEXT,
        reply_markup=keyboards.navigation(
            "home"
        ),
    )


# --------------------------------------------------
# About Command
# --------------------------------------------------


@Client.on_message(
    filters.command("about")
    & filters.private
)
async def about_command(
    client: Client,
    message: Message,
):

    await message.reply_text(
        ABOUT_TEXT,
        reply_markup=keyboards.navigation(
            "home"
        ),
    )


# --------------------------------------------------
# Callback Handler
# --------------------------------------------------


@Client.on_callback_query(
    filters.regex("^home$")
)
async def home_callback(
    client: Client,
    query: CallbackQuery,
):

    await query.message.edit_text(
        START_TEXT,
        reply_markup=keyboards.start(),
    )


@Client.on_callback_query(
    filters.regex("^help$")
)
async def help_callback(
    client: Client,
    query: CallbackQuery,
):

    await query.message.edit_text(
        HELP_TEXT,
        reply_markup=keyboards.navigation(
            "home"
        ),
    )


@Client.on_callback_query(
    filters.regex("^about$")
)
async def about_callback(
    client: Client,
    query: CallbackQuery,
):

    await query.message.edit_text(
        ABOUT_TEXT,
        reply_markup=keyboards.navigation(
            "home"
        ),
    )
