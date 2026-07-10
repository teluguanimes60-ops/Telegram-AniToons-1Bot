"""
database/settings.py

Global and user settings manager.

Part 1
"""

from __future__ import annotations

from typing import Any

from pymongo import ASCENDING

from database.manager import db
from logger import get_logger

log = get_logger(__name__)


class SettingsDatabase:
    """Settings Collection Manager."""

    def __init__(self) -> None:
        self.collection = db.settings

    async def create_indexes(self) -> None:
        """Create MongoDB indexes."""

        await self.collection.create_index(
            [("key", ASCENDING)],
            unique=True,
        )

        log.info("Settings indexes created.")

    # --------------------------------------------------
    # Default Settings
    # --------------------------------------------------

    DEFAULTS: dict[str, Any] = {
        "language": "en",
        "theme": "default",
        "max_active_users": 20,
        "max_queue_size": 1000,
        "force_subscribe": False,
        "maintenance_mode": False,
        "auto_thumbnail": True,
        "auto_caption": True,
        "auto_rename": False,
        "preferred_quality": "original",
        "preferred_format": "mp4",
        "notifications": True,
    }

    # --------------------------------------------------
    # Generic Methods
    # --------------------------------------------------

    async def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        document = await self.collection.find_one(
            {"key": key}
        )

        if document:
            return document["value"]

        if default is not None:
            return default

        return self.DEFAULTS.get(key)

    async def set(
        self,
        key: str,
        value: Any,
    ) -> None:

        await self.collection.update_one(
            {"key": key},
            {
                "$set": {
                    "value": value,
                }
            },
            upsert=True,
        )

    async def delete(
        self,
        key: str,
    ) -> bool:

        result = await self.collection.delete_one(
            {
                "key": key,
            }
        )

        return result.deleted_count > 0

    async def exists(
        self,
        key: str,
    ) -> bool:

        return (
            await self.collection.count_documents(
                {"key": key},
                limit=1,
            )
            > 0
        )

    async def all(self) -> dict[str, Any]:
        settings: dict[str, Any] = {}

        async for item in self.collection.find({}):
            settings[item["key"]] = item["value"]

        return settings


settings_db = SettingsDatabase()

              # --------------------------------------------------
    # Force Subscribe
    # --------------------------------------------------

    async def force_subscribe_enabled(self) -> bool:
        return await self.get(
            "force_subscribe",
            self.DEFAULTS["force_subscribe"],
        )

    async def set_force_subscribe(
        self,
        enabled: bool,
    ) -> None:
        await self.set(
            "force_subscribe",
            enabled,
        )

    # --------------------------------------------------
    # Maintenance Mode
    # --------------------------------------------------

    async def maintenance_enabled(self) -> bool:
        return await self.get(
            "maintenance_mode",
            self.DEFAULTS["maintenance_mode"],
        )

    async def set_maintenance(
        self,
        enabled: bool,
    ) -> None:
        await self.set(
            "maintenance_mode",
            enabled,
        )

    # --------------------------------------------------
    # Queue Settings
    # --------------------------------------------------

    async def get_max_active_users(self) -> int:
        return int(
            await self.get(
                "max_active_users",
                self.DEFAULTS["max_active_users"],
            )
        )

    async def set_max_active_users(
        self,
        value: int,
    ) -> None:
        await self.set(
            "max_active_users",
            value,
        )

    async def get_max_queue_size(self) -> int:
        return int(
            await self.get(
                "max_queue_size",
                self.DEFAULTS["max_queue_size"],
            )
        )

    async def set_max_queue_size(
        self,
        value: int,
    ) -> None:
        await self.set(
            "max_queue_size",
            value,
        )

    # --------------------------------------------------
    # Default Language
    # --------------------------------------------------

    async def get_default_language(self) -> str:
        return await self.get(
            "language",
            self.DEFAULTS["language"],
        )

    async def set_default_language(
        self,
        language: str,
    ) -> None:
        await self.set(
            "language",
            language,
        )

    # --------------------------------------------------
    # Default Theme
    # --------------------------------------------------

    async def get_default_theme(self) -> str:
        return await self.get(
            "theme",
            self.DEFAULTS["theme"],
        )

    async def set_default_theme(
        self,
        theme: str,
    ) -> None:
        await self.set(
            "theme",
            theme,
        )

    # --------------------------------------------------
    # Notifications
    # --------------------------------------------------

    async def notifications_enabled(self) -> bool:
        return await self.get(
            "notifications",
            self.DEFAULTS["notifications"],
        )

    async def set_notifications(
        self,
        enabled: bool,
    ) -> None:
        await self.set(
            "notifications",
            enabled,
        )

    # --------------------------------------------------
    # Auto Rename
    # --------------------------------------------------

    async def auto_rename_enabled(self) -> bool:
        return await self.get(
            "auto_rename",
            self.DEFAULTS["auto_rename"],
        )

    async def set_auto_rename(
        self,
        enabled: bool,
    ) -> None:
        await self.set(
            "auto_rename",
            enabled,
        )

    # --------------------------------------------------
    # Auto Caption
    # --------------------------------------------------

    async def auto_caption_enabled(self) -> bool:
        return await self.get(
            "auto_caption",
            self.DEFAULTS["auto_caption"],
        )

    async def set_auto_caption(
        self,
        enabled: bool,
    ) -> None:
        await self.set(
            "auto_caption",
            enabled,
        )

    # --------------------------------------------------
    # Auto Thumbnail
    # --------------------------------------------------

    async def auto_thumbnail_enabled(self) -> bool:
        return await self.get(
            "auto_thumbnail",
            self.DEFAULTS["auto_thumbnail"],
        )

    async def set_auto_thumbnail(
        self,
        enabled: bool,
    ) -> None:
        await self.set(
            "auto_thumbnail",
            enabled,
        )

    # --------------------------------------------------
    # Preferred Video Quality
    # --------------------------------------------------

    async def get_preferred_quality(self) -> str:
        return await self.get(
            "preferred_quality",
            self.DEFAULTS["preferred_quality"],
        )

    async def set_preferred_quality(
        self,
        quality: str,
    ) -> None:
        await self.set(
            "preferred_quality",
            quality,
        )

    # --------------------------------------------------
    # Preferred Output Format
    # --------------------------------------------------

    async def get_preferred_format(self) -> str:
        return await self.get(
            "preferred_format",
            self.DEFAULTS["preferred_format"],
        )

    async def set_preferred_format(
        self,
        fmt: str,
    ) -> None:
        await self.set(
            "preferred_format",
            fmt,
        )

    # --------------------------------------------------
    # Compression Level
    # --------------------------------------------------

    async def get_compression_level(self) -> str:
        return await self.get(
            "compression_level",
            "medium",
        )

    async def set_compression_level(
        self,
        level: str,
    ) -> None:
        await self.set(
            "compression_level",
            level,
        )

    # --------------------------------------------------
    # Upload Settings
    # --------------------------------------------------

    async def stream_uploads(self) -> bool:
        return await self.get(
            "stream_uploads",
            True,
        )

    async def set_stream_uploads(
        self,
        enabled: bool,
    ) -> None:
        await self.set(
            "stream_uploads",
            enabled,
        )

    async def delete_after_upload(self) -> bool:
        return await self.get(
            "delete_after_upload",
            True,
        )

    async def set_delete_after_upload(
        self,
        enabled: bool,
    ) -> None:
        await self.set(
            "delete_after_upload",
            enabled,
        )

    # --------------------------------------------------
    # Broadcast
    # --------------------------------------------------

    async def get_broadcast_delay(self) -> int:
        return int(
            await self.get(
                "broadcast_delay",
                1,
            )
        )

    async def set_broadcast_delay(
        self,
        seconds: int,
    ) -> None:
        await self.set(
            "broadcast_delay",
            seconds,
        )

    async def get_broadcast_batch_size(self) -> int:
        return int(
            await self.get(
                "broadcast_batch_size",
                100,
            )
        )

    async def set_broadcast_batch_size(
        self,
        value: int,
    ) -> None:
        await self.set(
            "broadcast_batch_size",
            value,
        )

    # --------------------------------------------------
    # Auto Join Request
    # --------------------------------------------------

    async def auto_request_enabled(self) -> bool:
        return await self.get(
            "auto_request_enabled",
            False,
        )

    async def set_auto_request(
        self,
        enabled: bool,
    ) -> None:
        await self.set(
            "auto_request_enabled",
            enabled,
        )

    async def auto_request_delay(self) -> int:
        return int(
            await self.get(
                "auto_request_delay",
                0,
            )
        )

    async def set_auto_request_delay(
        self,
        seconds: int,
    ) -> None:
        await self.set(
            "auto_request_delay",
            seconds,
        )

    # --------------------------------------------------
    # Auto Reactions
    # --------------------------------------------------

    async def auto_reaction_enabled(self) -> bool:
        return await self.get(
            "auto_reaction_enabled",
            False,
        )

    async def set_auto_reaction(
        self,
        enabled: bool,
    ) -> None:
        await self.set(
            "auto_reaction_enabled",
            enabled,
        )

    async def get_reaction_emoji(self) -> str:
        return await self.get(
            "reaction_emoji",
            "❤️",
        )

    async def set_reaction_emoji(
        self,
        emoji: str,
    ) -> None:
        await self.set(
            "reaction_emoji",
            emoji,
        )

    # --------------------------------------------------
    # Statistics
    # --------------------------------------------------

    async def statistics_enabled(self) -> bool:
        return await self.get(
            "statistics_enabled",
            True,
        )

    async def set_statistics(
        self,
        enabled: bool,
    ) -> None:
        await self.set(
            "statistics_enabled",
            enabled,
        )

    # --------------------------------------------------
    # Utilities
    # --------------------------------------------------

    async def reset_defaults(self) -> None:
        """
        Reset all global settings to their defaults.
        """

        for key, value in self.DEFAULTS.items():
            await self.set(
                key,
                value,
            )

        log.info("Global settings reset.")

    async def bulk_update(
        self,
        values: dict[str, Any],
    ) -> None:
        """
        Update multiple settings.
        """

        for key, value in values.items():
            await self.set(
                key,
                value,
            )

        log.info(
            "Updated %d settings.",
            len(values),
        )

