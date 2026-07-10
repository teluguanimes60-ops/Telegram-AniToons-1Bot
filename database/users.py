"""
database/users.py

Part 1

User database manager.

Includes:
- Create User
- Get User
- User Exists
- Update User
- Delete User
- Last Activity
- Basic Statistics
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError

from database import db
from logger import get_logger

log = get_logger(__name__)


class UsersDatabase:
    """Users Collection Manager."""

    def __init__(self) -> None:
        self.collection = db.users

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    @staticmethod
    def now() -> datetime:
        return datetime.now(timezone.utc)

    # ---------------------------------------------------------
    # Indexes
    # ---------------------------------------------------------

    async def create_indexes(self) -> None:
        """Create MongoDB indexes."""

        await self.collection.create_index(
            [("user_id", ASCENDING)],
            unique=True,
        )

        await self.collection.create_index(
            [("username", ASCENDING)],
        )

        await self.collection.create_index(
            [("premium", ASCENDING)],
        )

        await self.collection.create_index(
            [("last_activity", ASCENDING)],
        )

        log.info("Users indexes created.")

    # ---------------------------------------------------------
    # Default User Document
    # ---------------------------------------------------------

    def default_user(
        self,
        user_id: int,
        first_name: str,
        username: str | None = None,
    ) -> dict[str, Any]:

        return {
            "user_id": user_id,
            "first_name": first_name,
            "username": username,
            "premium": False,
            "premium_until": None,
            "language": "en",
            "theme": "default",
            "created_at": self.now(),
            "last_activity": self.now(),
            "total_files": 0,
            "total_downloads": 0,
            "total_uploads": 0,
            "total_conversions": 0,
            "is_banned": False,
        }

    # ---------------------------------------------------------
    # Create User
    # ---------------------------------------------------------

    async def create_user(
        self,
        user_id: int,
        first_name: str,
        username: str | None = None,
    ) -> bool:
        """Create new user."""

        document = self.default_user(
            user_id=user_id,
            first_name=first_name,
            username=username,
        )

        try:
            await self.collection.insert_one(document)

            log.info(
                "New user registered: %s",
                user_id,
            )

            return True

        except DuplicateKeyError:
            return False

    # ---------------------------------------------------------
    # Get User
    # ---------------------------------------------------------

    async def get_user(
        self,
        user_id: int,
    ) -> dict[str, Any] | None:
        """Return user document."""

        return await self.collection.find_one(
            {
                "user_id": user_id,
            }
        )

    # ---------------------------------------------------------
    # User Exists
    # ---------------------------------------------------------

    async def exists(
        self,
        user_id: int,
    ) -> bool:

        return (
            await self.collection.count_documents(
                {
                    "user_id": user_id,
                },
                limit=1,
            )
            > 0
        )

    # ---------------------------------------------------------
    # Update User
    # ---------------------------------------------------------

    async def update_user(
        self,
        user_id: int,
        **fields: Any,
    ) -> bool:
        """Update user."""

        if not fields:
            return False

        fields["last_activity"] = self.now()

        result = await self.collection.update_one(
            {
                "user_id": user_id,
            },
            {
                "$set": fields,
            },
        )

        return result.modified_count > 0

    # ---------------------------------------------------------
    # Delete User
    # ---------------------------------------------------------

    async def delete_user(
        self,
        user_id: int,
    ) -> bool:

        result = await self.collection.delete_one(
            {
                "user_id": user_id,
            }
        )

        return result.deleted_count > 0

    # ---------------------------------------------------------
    # Last Activity
    # ---------------------------------------------------------

    async def update_activity(
        self,
        user_id: int,
    ) -> None:

        await self.collection.update_one(
            {
                "user_id": user_id,
            },
            {
                "$set": {
                    "last_activity": self.now(),
                }
            },
        )

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    async def increment_files(
        self,
        user_id: int,
    ) -> None:

        await self.collection.update_one(
            {
                "user_id": user_id,
            },
            {
                "$inc": {
                    "total_files": 1,
                },
                "$set": {
                    "last_activity": self.now(),
                },
            },
        )

    async def increment_downloads(
        self,
        user_id: int,
    ) -> None:

        await self.collection.update_one(
            {
                "user_id": user_id,
            },
            {
                "$inc": {
                    "total_downloads": 1,
                },
                "$set": {
                    "last_activity": self.now(),
                },
            },
        )

    async def increment_uploads(
        self,
        user_id: int,
    ) -> None:

        await self.collection.update_one(
            {
                "user_id": user_id,
            },
            {
                "$inc": {
                    "total_uploads": 1,
                },
                "$set": {
                    "last_activity": self.now(),
                },
            },
        )

    async def increment_conversions(
        self,
        user_id: int,
    ) -> None:

        await self.collection.update_one(
            {
                "user_id": user_id,
            },
            {
                "$inc": {
                    "total_conversions": 1,
                },
                "$set": {
                    "last_activity": self.now(),
                },
            },
        )


users_db = UsersDatabase()
