"""
helpers/rename.py

Filename generation helper.
"""

from __future__ import annotations

import re
from pathlib import Path

from database.settings import settings_db


INVALID_CHARS = r'[\\/:*?"<>|]'


class RenameHelper:
    """
    Generates filenames according to user settings.
    """

    def __init__(self) -> None:
        pass

    async def generate_filename(
        self,
        message,
        original_path: Path | None = None,
    ) -> str:

        user_id = message.from_user.id

        settings = await settings_db.get_user_settings(user_id)

        # ----------------------------------
        # Original filename
        # ----------------------------------

        if original_path:
            filename = original_path.stem
            extension = original_path.suffix
        else:

            media = (
                message.document
                or message.video
                or message.audio
                or message.animation
            )

            filename = "Telegram_File"
            extension = ""

            if media:

                if getattr(media, "file_name", None):

                    path = Path(media.file_name)

                    filename = path.stem
                    extension = path.suffix

        # ----------------------------------
        # Custom filename
        # ----------------------------------

        custom = settings.get("filename")

        if custom:
            filename = custom

        # ----------------------------------
        # Remove words
        # ----------------------------------

        remove_words = settings.get(
            "remove_words",
            [],
        )

        for word in remove_words:

            filename = filename.replace(
                word,
                "",
            )

        # ----------------------------------
        # Replace words
        # ----------------------------------

        replace_words = settings.get(
            "replace_words",
            {},
        )

        for old, new in replace_words.items():

            filename = filename.replace(
                old,
                new,
            )

        # ----------------------------------
        # Prefix
        # ----------------------------------

        prefix = settings.get("prefix")

        if prefix:

            filename = f"{prefix}{filename}"

        # ----------------------------------
        # Suffix
        # ----------------------------------

        suffix = settings.get("suffix")

        if suffix:

            filename = f"{filename}{suffix}"

        # ----------------------------------
        # Numbering
        # ----------------------------------

        if settings.get("numbering"):

            number = settings.get(
                "number",
                1,
            )

            filename = f"{number:03d}_{filename}"

        # ----------------------------------
        # Cleanup
        # ----------------------------------

        filename = re.sub(
            INVALID_CHARS,
            "_",
            filename,
        )

        filename = re.sub(
            r"\s+",
            " ",
            filename,
        ).strip()

        if not filename:

            filename = "Telegram_File"

        return filename + extension

    async def preview(
        self,
        message,
        original_path: Path | None = None,
    ) -> str:

        return await self.generate_filename(
            message,
            original_path,
        )
