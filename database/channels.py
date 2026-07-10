"""
database/channels.py

Channel database manager.

Part 1
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pymongo import ASCENDING

from core.database import db
from logger import get_logger

log = get_logger(__name__)


class ChannelsDatabase:
    """Channels collection manager."""

    def __init__(self) -> None:
        self.collection = db.channels

    @staticmethod
    def now() -> datetime:
        return datetime.now(timezone.utc)

    # --------------------------------------------------
    # Indexes
    # --------------------------------------------------

    async def create_indexes(self) -> None:
        await self.collection.create_index(
            [("channel_id", ASCENDING)],
            unique=True,
        )

        await self.collection.create_index(
            [("enabled", ASCENDING)],
        )

        await self.collection.create_index(
            [("order", ASCENDING)],
        )

        log.info("Channel indexes created.")

    # --------------------------------------------------
    # Default Channel Document
    # --------------------------------------------------

    def default_channel(
        self,
        channel_id: int,
        title: str,
        username: str | None = None,
    ) -> dict[str, Any]:

        return {
            "channel_id": channel_id,
            "title": title,
            "username": username,
            "enabled": True,
            "force_subscribe": True,
            "auto_request": False,
            "auto_reaction": False,
            "reaction_emoji": "❤️",
            "order": 0,
            "created_at": self.now(),
            "updated_at": self.now(),
        }

    # --------------------------------------------------
    # Add Channel
    # --------------------------------------------------

    async def add_channel(
        self,
        channel_id: int,
        title: str,
        username: str | None = None,
    ) -> bool:

        if await self.exists(channel_id):
            return False

        document = self.default_channel(
            channel_id,
            title,
            username,
        )

        await self.collection.insert_one(document)

        log.info(
            "Channel added: %s",
            channel_id,
        )

        return True

    # --------------------------------------------------
    # Get Channel
    # --------------------------------------------------

    async def get_channel(
        self,
        channel_id: int,
    ) -> dict[str, Any] | None:

        return await self.collection.find_one(
            {
                "channel_id": channel_id,
            }
        )

    # --------------------------------------------------
    # Exists
    # --------------------------------------------------

    async def exists(
        self,
        channel_id: int,
    ) -> bool:

        return (
            await self.collection.count_documents(
                {
                    "channel_id": channel_id,
                },
                limit=1,
            )
            > 0
        )

    # --------------------------------------------------
    # Update
    # --------------------------------------------------

    async def update_channel(
        self,
        channel_id: int,
        **fields: Any,
    ) -> bool:

        if not fields:
            return False

        fields["updated_at"] = self.now()

        result = await self.collection.update_one(
            {
                "channel_id": channel_id,
            },
            {
                "$set": fields,
            },
        )

        return result.modified_count > 0

    # --------------------------------------------------
    # Delete
    # --------------------------------------------------

    async def delete_channel(
        self,
        channel_id: int,
    ) -> bool:

        result = await self.collection.delete_one(
            {
                "channel_id": channel_id,
            }
        )

        return result.deleted_count > 0


channels_db = ChannelsDatabase()

    # --------------------------------------------------
    # Enable / Disable
    # --------------------------------------------------

    async def enable_channel(
        self,
        channel_id: int,
    ) -> bool:

        return await self.update_channel(
            channel_id,
            enabled=True,
        )

    async def disable_channel(
        self,
        channel_id: int,
    ) -> bool:

        return await self.update_channel(
            channel_id,
            enabled=False,
        )

    async def is_enabled(
        self,
        channel_id: int,
    ) -> bool:

        channel = await self.get_channel(channel_id)

        if not channel:
            return False

        return channel.get(
            "enabled",
            False,
        )

    # --------------------------------------------------
    # Force Subscribe
    # --------------------------------------------------

    async def enable_force_subscribe(
        self,
        channel_id: int,
    ) -> bool:

        return await self.update_channel(
            channel_id,
            force_subscribe=True,
        )

    async def disable_force_subscribe(
        self,
        channel_id: int,
    ) -> bool:

        return await self.update_channel(
            channel_id,
            force_subscribe=False,
        )

    async def force_subscribe_enabled(
        self,
        channel_id: int,
    ) -> bool:

        channel = await self.get_channel(channel_id)

        if not channel:
            return False

        return channel.get(
            "force_subscribe",
            False,
        )

    # --------------------------------------------------
    # Auto Join Request
    # --------------------------------------------------

    async def enable_auto_request(
        self,
        channel_id: int,
    ) -> bool:

        return await self.update_channel(
            channel_id,
            auto_request=True,
        )

    async def disable_auto_request(
        self,
        channel_id: int,
    ) -> bool:

        return await self.update_channel(
            channel_id,
            auto_request=False,
        )

    async def auto_request_enabled(
        self,
        channel_id: int,
    ) -> bool:

        channel = await self.get_channel(channel_id)

        if not channel:
            return False

        return channel.get(
            "auto_request",
            False,
        )

    # --------------------------------------------------
    # Auto Reaction
    # --------------------------------------------------

    async def enable_auto_reaction(
        self,
        channel_id: int,
    ) -> bool:

        return await self.update_channel(
            channel_id,
            auto_reaction=True,
        )

    async def disable_auto_reaction(
        self,
        channel_id: int,
    ) -> bool:

        return await self.update_channel(
            channel_id,
            auto_reaction=False,
        )

    async def auto_reaction_enabled(
        self,
        channel_id: int,
    ) -> bool:

        channel = await self.get_channel(channel_id)

        if not channel:
            return False

        return channel.get(
            "auto_reaction",
            False,
        )

    async def set_reaction_emoji(
        self,
        channel_id: int,
        emoji: str,
    ) -> bool:

        return await self.update_channel(
            channel_id,
            reaction_emoji=emoji,
        )

    async def get_reaction_emoji(
        self,
        channel_id: int,
    ) -> str:

        channel = await self.get_channel(channel_id)

        if not channel:
            return "❤️"

        return channel.get(
            "reaction_emoji",
            "❤️",
        )

    # --------------------------------------------------
    # Channel Order
    # --------------------------------------------------

    async def set_order(
        self,
        channel_id: int,
        order: int,
    ) -> bool:

        return await self.update_channel(
            channel_id,
            order=order,
        )

    async def get_order(
        self,
        channel_id: int,
    ) -> int:

        channel = await self.get_channel(channel_id)

        if not channel:
            return 0

        return channel.get(
            "order",
            0,
        )

    # --------------------------------------------------
    # Lists
    # --------------------------------------------------

    async def get_enabled_channels(
        self,
    ) -> list[dict[str, Any]]:

        cursor = (
            self.collection
            .find(
                {
                    "enabled": True,
                }
            )
            .sort("order", 1)
        )

        return await cursor.to_list(length=None)

    async def get_force_subscribe_channels(
        self,
    ) -> list[dict[str, Any]]:

        cursor = (
            self.collection
            .find(
                {
                    "enabled": True,
                    "force_subscribe": True,
                }
            )
            .sort("order", 1)
        )

        return await cursor.to_list(length=None)

    async def list_channels(
        self,
        page: int = 1,
        limit: int = 20,
    ) -> list[dict[str, Any]]:

        skip = (page - 1) * limit

        cursor = (
            self.collection
            .find({})
            .sort("order", 1)
            .skip(skip)
            .limit(limit)
        )

        return await cursor.to_list(length=limit)

    # --------------------------------------------------
    # Statistics
    # --------------------------------------------------

    async def total_channels(self) -> int:

        return await self.collection.count_documents({})

    async def total_enabled_channels(self) -> int:

        return await self.collection.count_documents(
            {
                "enabled": True,
            }
        )

    async def total_force_subscribe_channels(self) -> int:

        return await self.collection.count_documents(
            {
                "enabled": True,
                "force_subscribe": True,
            }
        )

    # --------------------------------------------------
    # Search
    # --------------------------------------------------

    async def search_channels(
        self,
        keyword: str,
        limit: int = 20,
    ) -> list[dict[str, Any]]:

        cursor = self.collection.find(
            {
                "$or": [
                    {
                        "title": {
                            "$regex": keyword,
                            "$options": "i",
                        }
                    },
                    {
                        "username": {
                            "$regex": keyword,
                            "$options": "i",
                        }
                    },
                ]
            }
        ).limit(limit)

        return await cursor.to_list(length=limit)

    # --------------------------------------------------
    # File Index
    # --------------------------------------------------

    async def enable_file_index(
        self,
        channel_id: int,
    ) -> bool:

        return await self.update_channel(
            channel_id,
            file_index=True,
        )

    async def disable_file_index(
        self,
        channel_id: int,
    ) -> bool:

        return await self.update_channel(
            channel_id,
            file_index=False,
        )

    async def file_index_enabled(
        self,
        channel_id: int,
    ) -> bool:

        channel = await self.get_channel(channel_id)

        if not channel:
            return False

        return channel.get(
            "file_index",
            False,
        )

    async def indexed_channels(
        self,
    ) -> list[dict[str, Any]]:

        cursor = self.collection.find(
            {
                "file_index": True,
                "enabled": True,
            }
        ).sort("order", 1)

        return await cursor.to_list(length=None)

    # --------------------------------------------------
    # Bulk Operations
    # --------------------------------------------------

    async def enable_all(self) -> int:

        result = await self.collection.update_many(
            {},
            {
                "$set": {
                    "enabled": True,
                    "updated_at": self.now(),
                }
            },
        )

        return result.modified_count

    async def disable_all(self) -> int:

        result = await self.collection.update_many(
            {},
            {
                "$set": {
                    "enabled": False,
                    "updated_at": self.now(),
                }
            },
        )

        return result.modified_count

    async def delete_all(self) -> int:

        result = await self.collection.delete_many({})

        return result.deleted_count

    # --------------------------------------------------
    # Broadcast Helper
    # --------------------------------------------------

    async def broadcast_channels(
        self,
    ) -> list[int]:

        channels = []

        async for channel in self.collection.find(
            {
                "enabled": True,
            },
            {
                "_id": 0,
                "channel_id": 1,
            },
        ):
            channels.append(channel["channel_id"])

        return channels

    # --------------------------------------------------
    # Dashboard Stats
    # --------------------------------------------------

    async def stats(self) -> dict[str, int]:

        return {
            "total": await self.total_channels(),
            "enabled": await self.total_enabled_channels(),
            "force_subscribe": await self.total_force_subscribe_channels(),
            "indexed": await self.collection.count_documents(
                {
                    "file_index": True,
                }
            ),
        }


channels_db = ChannelsDatabase()
