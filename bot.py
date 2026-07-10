"""
bot.py

Creates and exports the global Pyrogram Client.
"""

from __future__ import annotations

from pyrogram import Client
from pyrogram.enums import ParseMode

from config import config

bot = Client(
    name="AniToonBot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
    parse_mode=ParseMode.HTML,
    workers=32,
    sleep_threshold=30,
    max_concurrent_transmissions=8,
    no_updates=False,
)
