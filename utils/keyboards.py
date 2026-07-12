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

# ------------------------------------------
# Quality Selection
# ------------------------------------------

class Keyboards:

    @staticmethod
    def quality_menu(
        available: list[int],
    ) -> InlineKeyboardMarkup:

        rows = []
        row = []

        for quality in sorted(
            available,
            reverse=True,
        ):

            row.append(
                InlineKeyboardButton(
                    f"{quality}p",
                    callback_data=f"quality:{quality}",
                )
            )

            if len(row) == 2:
                rows.append(row)
                row = []

        if row:
            rows.append(row)

        rows.append(
            [
                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="convert_menu",
                ),
                InlineKeyboardButton(
                    "🏠 Home",
                    callback_data="home",
                ),
            ]
        )

        return InlineKeyboardMarkup(rows)

    # ------------------------------------------
    # Format Selection
    # ------------------------------------------

    @staticmethod
    def format_menu():

        formats = [
            "MP4",
            "MKV",
            "AVI",
            "MOV",
            "WEBM",
            "TS",
        ]

        rows = []

        for i in range(0, len(formats), 2):

            row = []

            for fmt in formats[i:i + 2]:

                row.append(
                    InlineKeyboardButton(
                        fmt,
                        callback_data=f"format:{fmt.lower()}",
                    )
                )

            rows.append(row)

        rows.append(
            [
                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="convert_menu",
                ),
                InlineKeyboardButton(
                    "🏠 Home",
                    callback_data="home",
                ),
            ]
        )

        return InlineKeyboardMarkup(rows)

    # ------------------------------------------
    # Compression
    # ------------------------------------------

    @staticmethod
    def compression_menu():

        return InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Low",
                        callback_data="compress:low",
                    ),
                    InlineKeyboardButton(
                        "Medium",
                        callback_data="compress:medium",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "High",
                        callback_data="compress:high",
                    ),
                    InlineKeyboardButton(
                        "Extreme",
                        callback_data="compress:extreme",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "⬅️ Back",
                        callback_data="convert_menu",
                    ),
                    InlineKeyboardButton(
                        "🏠 Home",
                        callback_data="home",
                    ),
                ],
            ]
        )

    # ------------------------------------------
    # Thumbnail Menu
    # ------------------------------------------

    @staticmethod
    def thumbnail_menu():

        return InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "📤 Upload",
                        callback_data="thumb_upload",
                    ),
                    InlineKeyboardButton(
                        "🖼 Auto",
                        callback_data="thumb_auto",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "🗑 Remove",
                        callback_data="thumb_remove",
                    ),
                    InlineKeyboardButton(
                        "👀 Preview",
                        callback_data="thumb_preview",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "⬅️ Back",
                        callback_data="settings",
                    ),
                    InlineKeyboardButton(
                        "🏠 Home",
                        callback_data="home",
                    ),
                ],
            ]
        )

    # ------------------------------------------
    # Settings
    # ------------------------------------------

    @staticmethod
    def settings_menu():

        return InlineKeyboardMarkup(
            [
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
                        "🌐 Language",
                        callback_data="language",
                    ),
                    InlineKeyboardButton(
                        "🎨 Theme",
                        callback_data="theme",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "⬅️ Back",
                        callback_data="home",
                    ),
                ],
            ]
        )

# ------------------------------------------
# Force Subscribe
# ------------------------------------------

class Keyboards:

    @staticmethod
    def force_subscribe(
        channels: list[tuple[str, str]],
    ) -> InlineKeyboardMarkup:

        rows = []

        for name, url in channels:

            rows.append(
                [
                    InlineKeyboardButton(
                        f"📢 {name}",
                        url=url,
                    )
                ]
            )

        rows.append(
            [
                InlineKeyboardButton(
                    "🔄 Refresh",
                    callback_data="fsub_refresh",
                ),
                InlineKeyboardButton(
                    "✅ Continue",
                    callback_data="fsub_continue",
                ),
            ]
        )

        return InlineKeyboardMarkup(rows)

    # ------------------------------------------
    # Queue Menu
    # ------------------------------------------

    @staticmethod
    def queue_menu(
        position: int,
    ) -> InlineKeyboardMarkup:

        return InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        f"📍 Position #{position}",
                        callback_data="queue_info",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "❌ Cancel Job",
                        callback_data="queue_cancel",
                    ),
                ],
            ]
        )

    # ------------------------------------------
    # Premium Menu
    # ------------------------------------------

    @staticmethod
    def premium_menu():

        return InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "⭐ Buy Premium",
                        callback_data="premium_buy",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "💎 My Plan",
                        callback_data="premium_status",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "🏠 Home",
                        callback_data="home",
                    ),
                ],
            ]
        )

    # ------------------------------------------
    # Admin Panel
    # ------------------------------------------

    @staticmethod
    def admin_panel():

        return InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "📊 Statistics",
                        callback_data="admin_stats",
                    ),
                    InlineKeyboardButton(
                        "📢 Broadcast",
                        callback_data="admin_broadcast",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "👑 Premium",
                        callback_data="admin_premium",
                    ),
                    InlineKeyboardButton(
                        "👥 Users",
                        callback_data="admin_users",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "📺 Channels",
                        callback_data="admin_channels",
                    ),
                    InlineKeyboardButton(
                        "⏳ Queue",
                        callback_data="admin_queue",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "⚙ Settings",
                        callback_data="admin_settings",
                    ),
                    InlineKeyboardButton(
                        "📄 Logs",
                        callback_data="admin_logs",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "♻ Restart",
                        callback_data="admin_restart",
                    ),
                    InlineKeyboardButton(
                        "🛑 Shutdown",
                        callback_data="admin_shutdown",
                    ),
                ],
            ]
        )

    # ------------------------------------------
    # Broadcast
    # ------------------------------------------

    @staticmethod
    def broadcast_menu():

        return InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "📝 Text",
                        callback_data="broadcast_text",
                    ),
                    InlineKeyboardButton(
                        "🖼 Photo",
                        callback_data="broadcast_photo",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "🎥 Video",
                        callback_data="broadcast_video",
                    ),
                    InlineKeyboardButton(
                        "📄 Document",
                        callback_data="broadcast_document",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "❌ Cancel",
                        callback_data="home",
                    ),
                ],
            ]
        )

    # ------------------------------------------
    # Confirmation
    # ------------------------------------------

    @staticmethod
    def confirm(
        yes: str,
        no: str,
    ) -> InlineKeyboardMarkup:

        return InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "✅ Yes",
                        callback_data=yes,
                    ),
                    InlineKeyboardButton(
                        "❌ No",
                        callback_data=no,
                    ),
                ]
            ]
        )

    # ------------------------------------------
    # Pagination
    # ------------------------------------------

    @staticmethod
    def pagination(
        page: int,
        pages: int,
        prefix: str,
    ) -> InlineKeyboardMarkup:

        buttons = []

        if page > 1:

            buttons.append(
                InlineKeyboardButton(
                    "⬅",
                    callback_data=f"{prefix}:{page-1}",
                )
            )

        buttons.append(
            InlineKeyboardButton(
                f"{page}/{pages}",
                callback_data="ignore",
            )
        )

        if page < pages:

            buttons.append(
                InlineKeyboardButton(
                    "➡",
                    callback_data=f"{prefix}:{page+1}",
                )
            )

        return InlineKeyboardMarkup([buttons])
