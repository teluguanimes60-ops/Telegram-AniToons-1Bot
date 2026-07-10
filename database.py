"""
database.py

Async MongoDB manager for AniToon Bot.
"""

from __future__ import annotations

from typing import Optional

from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorCollection,
    AsyncIOMotorDatabase,
)

from config import config
from logger import get_logger

log = get_logger(__name__)


class Database:
    """MongoDB manager."""

    def __init__(self) -> None:
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None

        self.users: Optional[AsyncIOMotorCollection] = None
        self.settings: Optional[AsyncIOMotorCollection] = None
        self.premium: Optional[AsyncIOMotorCollection] = None
        self.queue: Optional[AsyncIOMotorCollection] = None
        self.logs: Optional[AsyncIOMotorCollection] = None
        self.channels: Optional[AsyncIOMotorCollection] = None
        self.thumbnails: Optional[AsyncIOMotorCollection] = None
        self.captions: Optional[AsyncIOMotorCollection] = None
        self.statistics: Optional[AsyncIOMotorCollection] = None
        self.requests: Optional[AsyncIOMotorCollection] = None
        self.rename_templates: Optional[AsyncIOMotorCollection] = None
        self.converter_settings: Optional[AsyncIOMotorCollection] = None
        self.download_history: Optional[AsyncIOMotorCollection] = None
        self.broadcast_history: Optional[AsyncIOMotorCollection] = None

    async def connect(self) -> None:
        """Connect to MongoDB."""

        if self.client is not None:
            return

        self.client = AsyncIOMotorClient(
            config.MONGO_URI,
            serverSelectionTimeoutMS=10000,
        )

        self.db = self.client[config.DATABASE_NAME]

        self.users = self.db.users
        self.settings = self.db.settings
        self.premium = self.db.premium
        self.queue = self.db.queue
        self.logs = self.db.logs
        self.channels = self.db.channels
        self.thumbnails = self.db.thumbnails
        self.captions = self.db.captions
        self.statistics = self.db.statistics
        self.requests = self.db.requests
        self.rename_templates = self.db.rename_templates
        self.converter_settings = self.db.converter_settings
        self.download_history = self.db.download_history
        self.broadcast_history = self.db.broadcast_history

        await self.client.admin.command("ping")

        await self.create_indexes()

        log.info("MongoDB connected successfully.")

    async def disconnect(self) -> None:
        """Close MongoDB connection."""

        if self.client:
            self.client.close()
            self.client = None
            self.db = None

            log.info("MongoDB connection closed.")

    async def create_indexes(self) -> None:
        """Create indexes."""

        await self.users.create_index(
            "user_id",
            unique=True,
        )

        await self.settings.create_index(
            "user_id",
            unique=True,
        )

        await self.premium.create_index(
            "user_id",
            unique=True,
        )

        await self.channels.create_index(
            "channel_id",
            unique=True,
        )

        await self.statistics.create_index(
            "date",
        )

        await self.queue.create_index(
            "user_id",
        )

        await self.download_history.create_index(
            "user_id",
        )

        await self.broadcast_history.create_index(
            "broadcast_id",
            unique=True,
        )

        log.info("MongoDB indexes created.")

    async def health(self) -> bool:
        """Check database health."""

        try:
            await self.client.admin.command("ping")
            return True
        except Exception:
            return False


db = Database()
