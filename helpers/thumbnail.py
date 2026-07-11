"""
helpers/thumbnail.py

Thumbnail manager for AniToons Bot.
"""

from __future__ import annotations

import contextlib
from pathlib import Path

from database.settings import settings_db
from database.thumbnails import thumbnails_db

from ffmpeg.thumbnail import (
    generate_thumbnail,
    resize_thumbnail,
)


class ThumbnailHelper:
    """
    Handles user thumbnails.

    Modes
    -----
    • Manual
    • Auto
    • None
    """

    def __init__(self):
        pass

    # --------------------------------------------------
    # Public
    # --------------------------------------------------

    async def get_thumbnail(
        self,
        message,
        media_path: Path,
    ) -> Path | None:

        user_id = message.from_user.id

        settings = await settings_db.get_user_settings(
            user_id
        )

        mode = settings.get(
            "thumbnail_mode",
            "manual",
        )

        if mode == "none":
            return None

        if mode == "manual":

            thumb = await self.manual_thumbnail(
                user_id
            )

            if thumb:
                return thumb

        return await self.auto_thumbnail(
            media_path,
            settings,
        )

    # --------------------------------------------------
    # Manual Thumbnail
    # --------------------------------------------------

    async def manual_thumbnail(
        self,
        user_id: int,
    ) -> Path | None:

        data = await thumbnails_db.get_thumbnail(
            user_id
        )

        if not data:
            return None

        path = Path(data)

        if not path.exists():
            return None

        return path

    # --------------------------------------------------
    # Auto Thumbnail
    # --------------------------------------------------

    async def auto_thumbnail(
        self,
        media_path: Path,
        settings: dict,
    ) -> Path | None:

        thumb = await generate_thumbnail(
            media_path
        )

        if thumb is None:
            return None

        width = settings.get(
            "thumbnail_width",
            320,
        )

        height = settings.get(
            "thumbnail_height",
            180,
        )

        await resize_thumbnail(
            thumb,
            width,
            height,
        )

        return thumb

    # --------------------------------------------------
    # Delete
    # --------------------------------------------------

    async def delete(
        self,
        thumb: Path | None,
    ):

        if thumb is None:
            return

        with contextlib.suppress(Exception):

            if thumb.exists():
                thumb.unlink()

    # --------------------------------------------------
    # Exists
    # --------------------------------------------------

    async def exists(
        self,
        user_id: int,
    ) -> bool:

        thumb = await self.manual_thumbnail(
            user_id
        )

        return thumb is not None

    # --------------------------------------------------
    # Preview
    # --------------------------------------------------

    async def preview(
        self,
        message,
        media_path: Path,
    ) -> Path | None:

        return await self.get_thumbnail(
            message,
            media_path,
        )
