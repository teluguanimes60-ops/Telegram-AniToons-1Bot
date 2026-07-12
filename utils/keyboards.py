"""
utils/keyboards.py

Centralized inline keyboard builder.
"""

from __future__ import annotations

from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


class Keyboards:

    # ------------------------------------------
    # Navigation
    # ------------------------------------------

    @staticmethod
    def navigation(
        back: str = "home",
    ) -> InlineKeyboardMarkup:

        return InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "⬅️ Back",
                        callback_data=back,
                    ),
                    InlineKeyboardButton(
                        "🏠 Home",
                        callback_data="home",
                    ),
                ]
            ]
        )

    # ------------------------------------------
    # Start Menu
    # ------------------------------------------

    @staticmethod
    def start() -> InlineKeyboardMarkup:

        return InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "📝 Rename",
                        callback_data="rename_menu",
                    ),
                    InlineKeyboardButton(
                        "🎞 Convert",
                        callback_data="convert_menu",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "⚙️ Settings",
                        callback_data="settings",
                    ),
                    InlineKeyboardButton(
                        "❓ Help",
                        callback_data="help",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "ℹ️ About",
                        callback_data="about",
                    )
                ],
            ]
        )

    # ------------------------------------------
    # File Menu
    # ------------------------------------------

    @staticmethod
    def file_menu() -> InlineKeyboardMarkup:

        return InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "✏️ Rename",
                        callback_data="rename",
                    ),
                    InlineKeyboardButton(
                        "🎬 Convert",
                        callback_data="convert",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "🖼 Thumbnail",
                        callback_data="thumbnail",
                    ),
                    InlineKeyboardButton(
                        "📝 Caption",
                        callback_data="caption",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "❌ Cancel",
                        callback_data="cancel",
                    )
                ],
            ]
        )

    # ------------------------------------------
    # Progress Buttons
    # ------------------------------------------

    @staticmethod
    def progress() -> InlineKeyboardMarkup:

        return InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "⏸ Pause",
                        callback_data="pause",
                    ),
                    InlineKeyboardButton(
                        "▶ Resume",
                        callback_data="resume",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "❌ Cancel",
                        callback_data="cancel",
                    )
                ],
            ]
        )

    # ------------------------------------------
    # Upload Buttons
    # ------------------------------------------

    @staticmethod
    def upload() -> InlineKeyboardMarkup:

        return InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "❌ Cancel",
                        callback_data="cancel",
                    )
                ]
            ]
        )


keyboards = Keyboards()

