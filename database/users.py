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

# ---------------------------------------------------------
# Language
# ---------------------------------------------------------

    async def get_language(
        self,
        user_id: int,
    ) -> str:

        user = await self.get_user(user_id)

        if not user:
            return "en"

        return user.get("language", "en")


    async def set_language(
        self,
        user_id: int,
        language: str,
    ) -> bool:

        return await self.update_user(
            user_id,
            language=language,
        )


# ---------------------------------------------------------
# Theme
# ---------------------------------------------------------

    async def get_theme(
        self,
        user_id: int,
    ) -> str:

        user = await self.get_user(user_id)

        if not user:
            return "default"

        return user.get(
            "theme",
            "default",
        )


    async def set_theme(
        self,
        user_id: int,
        theme: str,
    ) -> bool:

        return await self.update_user(
            user_id,
            theme=theme,
        )


# ---------------------------------------------------------
# Caption
# ---------------------------------------------------------

    async def get_caption(
        self,
        user_id: int,
    ) -> str | None:

        user = await self.get_user(user_id)

        if not user:
            return None

        return user.get("caption")


    async def set_caption(
        self,
        user_id: int,
        caption: str,
    ) -> bool:

        return await self.update_user(
            user_id,
            caption=caption,
        )


    async def remove_caption(
        self,
        user_id: int,
    ) -> bool:

        result = await self.collection.update_one(
            {
                "user_id": user_id,
            },
            {
                "$unset": {
                    "caption": "",
                },
            },
        )

        return result.modified_count > 0


# ---------------------------------------------------------
# Thumbnail
# ---------------------------------------------------------

    async def get_thumbnail(
        self,
        user_id: int,
    ) -> str | None:

        user = await self.get_user(user_id)

        if not user:
            return None

        return user.get("thumbnail")


    async def set_thumbnail(
        self,
        user_id: int,
        file_id: str,
    ) -> bool:

        return await self.update_user(
            user_id,
            thumbnail=file_id,
        )


    async def remove_thumbnail(
        self,
        user_id: int,
    ) -> bool:

        result = await self.collection.update_one(
            {
                "user_id": user_id,
            },
            {
                "$unset": {
                    "thumbnail": "",
                },
            },
        )

        return result.modified_count > 0


# ---------------------------------------------------------
# Auto Thumbnail
# ---------------------------------------------------------

    async def auto_thumbnail_enabled(
        self,
        user_id: int,
    ) -> bool:

        user = await self.get_user(user_id)

        if not user:
            return True

        return user.get(
            "auto_thumbnail",
            True,
        )


    async def set_auto_thumbnail(
        self,
        user_id: int,
        enabled: bool,
    ) -> bool:

        return await self.update_user(
            user_id,
            auto_thumbnail=enabled,
        )


# ---------------------------------------------------------
# Auto Caption
# ---------------------------------------------------------

    async def auto_caption_enabled(
        self,
        user_id: int,
    ) -> bool:

        user = await self.get_user(user_id)

        if not user:
            return True

        return user.get(
            "auto_caption",
            True,
        )


    async def set_auto_caption(
        self,
        user_id: int,
        enabled: bool,
    ) -> bool:

        return await self.update_user(
            user_id,
            auto_caption=enabled,
        )


# ---------------------------------------------------------
# Auto Rename
# ---------------------------------------------------------

    async def auto_rename_enabled(
        self,
        user_id: int,
    ) -> bool:

        user = await self.get_user(user_id)

        if not user:
            return False

        return user.get(
            "auto_rename",
            False,
        )


    async def set_auto_rename(
        self,
        user_id: int,
        enabled: bool,
    ) -> bool:

        return await self.update_user(
            user_id,
            auto_rename=enabled,
        )


# ---------------------------------------------------------
# Rename Template
# ---------------------------------------------------------

    async def get_template(
        self,
        user_id: int,
    ) -> dict[str, Any]:

        user = await self.get_user(user_id)

        if not user:
            return {}

        return user.get(
            "rename_template",
            {},
        )


    async def set_template(
        self,
        user_id: int,
        template: dict[str, Any],
    ) -> bool:

        return await self.update_user(
            user_id,
            rename_template=template,
        )


# ---------------------------------------------------------
# Preferred Format
# ---------------------------------------------------------

    async def get_format(
        self,
        user_id: int,
    ) -> str:

        user = await self.get_user(user_id)

        if not user:
            return "mp4"

        return user.get(
            "preferred_format",
            "mp4",
        )


    async def set_format(
        self,
        user_id: int,
        fmt: str,
    ) -> bool:

        return await self.update_user(
            user_id,
            preferred_format=fmt,
        )


# ---------------------------------------------------------
# Preferred Quality
# ---------------------------------------------------------

    async def get_quality(
        self,
        user_id: int,
    ) -> str:

        user = await self.get_user(user_id)

        if not user:
            return "original"

        return user.get(
            "preferred_quality",
            "original",
        )


    async def set_quality(
        self,
        user_id: int,
        quality: str,
    ) -> bool:

        return await self.update_user(
            user_id,
            preferred_quality=quality,
        )


# ---------------------------------------------------------
# Notifications
# ---------------------------------------------------------

    async def notifications_enabled(
        self,
        user_id: int,
    ) -> bool:

        user = await self.get_user(user_id)

        if not user:
            return True

        return user.get(
            "notifications",
            True,
        )


    async def set_notifications(
        self,
        user_id: int,
        enabled: bool,
    ) -> bool:

        return await self.update_user(
            user_id,
            notifications=enabled,
        )

# ---------------------------------------------------------
# Premium Management
# ---------------------------------------------------------

    async def is_premium(
        self,
        user_id: int,
    ) -> bool:

        user = await self.get_user(user_id)

        if not user:
            return False

        if not user.get("premium", False):
            return False

        expiry = user.get("premium_until")

        if expiry is None:
            return True

        if expiry < self.now():
            await self.remove_premium(user_id)
            return False

        return True


    async def add_premium(
        self,
        user_id: int,
        expiry: datetime | None = None,
    ) -> bool:

        return await self.update_user(
            user_id,
            premium=True,
            premium_until=expiry,
        )


    async def remove_premium(
        self,
        user_id: int,
    ) -> bool:

        return await self.update_user(
            user_id,
            premium=False,
            premium_until=None,
        )


    async def get_premium_expiry(
        self,
        user_id: int,
    ) -> datetime | None:

        user = await self.get_user(user_id)

        if not user:
            return None

        return user.get("premium_until")


# ---------------------------------------------------------
# Ban Management
# ---------------------------------------------------------

    async def ban_user(
        self,
        user_id: int,
    ) -> bool:

        return await self.update_user(
            user_id,
            is_banned=True,
        )


    async def unban_user(
        self,
        user_id: int,
    ) -> bool:

        return await self.update_user(
            user_id,
            is_banned=False,
        )


    async def is_banned(
        self,
        user_id: int,
    ) -> bool:

        user = await self.get_user(user_id)

        if not user:
            return False

        return user.get("is_banned", False)


# ---------------------------------------------------------
# User Statistics
# ---------------------------------------------------------

    async def total_users(self) -> int:

        return await self.collection.count_documents({})


    async def total_premium_users(self) -> int:

        return await self.collection.count_documents(
            {
                "premium": True,
            }
        )


    async def total_banned_users(self) -> int:

        return await self.collection.count_documents(
            {
                "is_banned": True,
            }
        )


# ---------------------------------------------------------
# Search
# ---------------------------------------------------------

    async def search_users(
        self,
        keyword: str,
        limit: int = 20,
    ) -> list[dict[str, Any]]:

        cursor = self.collection.find(
            {
                "$or": [
                    {
                        "first_name": {
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


# ---------------------------------------------------------
# Pagination
# ---------------------------------------------------------

    async def get_users(
        self,
        page: int = 1,
        limit: int = 50,
    ) -> list[dict[str, Any]]:

        skip = (page - 1) * limit

        cursor = (
            self.collection
            .find({})
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )

        return await cursor.to_list(length=limit)


# ---------------------------------------------------------
# Recent Users
# ---------------------------------------------------------

    async def recent_users(
        self,
        limit: int = 20,
    ) -> list[dict[str, Any]]:

        cursor = (
            self.collection
            .find({})
            .sort("created_at", -1)
            .limit(limit)
        )

        return await cursor.to_list(length=limit)


# ---------------------------------------------------------
# Active Users
# ---------------------------------------------------------

    async def active_users(
        self,
        limit: int = 20,
    ) -> list[dict[str, Any]]:

        cursor = (
            self.collection
            .find({})
            .sort("last_activity", -1)
            .limit(limit)
        )

        return await cursor.to_list(length=limit)


# ---------------------------------------------------------
# Broadcast Helpers
# ---------------------------------------------------------

    async def all_user_ids(self):

        async for user in self.collection.find(
            {},
            {
                "_id": 0,
                "user_id": 1,
            },
        ):
            yield user["user_id"]


# ---------------------------------------------------------
# Delete All Users
# ---------------------------------------------------------

    async def delete_all_users(self) -> int:

        result = await self.collection.delete_many({})

        return result.deleted_count


# ---------------------------------------------------------
# Database Stats
# ---------------------------------------------------------

    async def stats(self) -> dict[str, int]:

        return {
            "users": await self.total_users(),
            "premium": await self.total_premium_users(),
            "banned": await self.total_banned_users(),
        }


# ---------------------------------------------------------
# Cleanup Premium
# ---------------------------------------------------------

    async def cleanup_expired_premium(self) -> int:

        result = await self.collection.update_many(
            {
                "premium": True,
                "premium_until": {
                    "$lt": self.now(),
                },
            },
            {
                "$set": {
                    "premium": False,
                    "premium_until": None,
                },
            },
        )

        return result.modified_count
