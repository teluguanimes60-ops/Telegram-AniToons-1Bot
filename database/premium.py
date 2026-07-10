"""
database/premium.py

Premium subscription manager.

Part 1
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from pymongo import ASCENDING

from database.manager import db
from logger import get_logger

log = get_logger(__name__)


class PremiumDatabase:
    """Premium users collection manager."""

    def __init__(self) -> None:
        self.collection = db.premium

    @staticmethod
    def now() -> datetime:
        return datetime.now(timezone.utc)

    async def create_indexes(self) -> None:
        """Create MongoDB indexes."""

        await self.collection.create_index(
            [("user_id", ASCENDING)],
            unique=True,
        )

        await self.collection.create_index(
            [("expires_at", ASCENDING)],
        )

        await self.collection.create_index(
            [("plan", ASCENDING)],
        )

        log.info("Premium indexes created.")

    # --------------------------------------------------
    # Plans
    # --------------------------------------------------

    PLANS = {
        "monthly": 30,
        "yearly": 365,
        "lifetime": None,
    }

    # --------------------------------------------------
    # Create / Update Premium
    # --------------------------------------------------

    async def add_premium(
        self,
        user_id: int,
        plan: str,
        added_by: int,
    ) -> dict[str, Any]:
        """
        Add or renew premium.
        """

        if plan not in self.PLANS:
            raise ValueError(f"Invalid premium plan: {plan}")

        now = self.now()

        expires_at = (
            None
            if self.PLANS[plan] is None
            else now + timedelta(days=self.PLANS[plan])
        )

        document = {
            "user_id": user_id,
            "plan": plan,
            "added_by": added_by,
            "created_at": now,
            "updated_at": now,
            "expires_at": expires_at,
            "active": True,
        }

        await self.collection.update_one(
            {"user_id": user_id},
            {"$set": document},
            upsert=True,
        )

        log.info(
            "Premium added: user=%s plan=%s",
            user_id,
            plan,
        )

        return document

    # --------------------------------------------------
    # Get Premium
    # --------------------------------------------------

    async def get_premium(
        self,
        user_id: int,
    ) -> dict[str, Any] | None:

        return await self.collection.find_one(
            {
                "user_id": user_id,
            }
        )

    # --------------------------------------------------
    # Exists
    # --------------------------------------------------

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

    # --------------------------------------------------
    # Remove Premium
    # --------------------------------------------------

    async def remove_premium(
        self,
        user_id: int,
    ) -> bool:

        result = await self.collection.delete_one(
            {
                "user_id": user_id,
            }
        )

        return result.deleted_count > 0

      # --------------------------------------------------
    # Premium Status
    # --------------------------------------------------

    async def is_premium(
        self,
        user_id: int,
    ) -> bool:
        """
        Check whether the user currently has an active premium subscription.
        Automatically expires outdated subscriptions.
        """

        premium = await self.get_premium(user_id)

        if premium is None:
            return False

        if not premium.get("active", False):
            return False

        expires_at = premium.get("expires_at")

        if expires_at is None:
            return True

        if expires_at <= self.now():
            await self.expire_premium(user_id)
            return False

        return True

    # --------------------------------------------------
    # Expire Premium
    # --------------------------------------------------

    async def expire_premium(
        self,
        user_id: int,
    ) -> bool:
        """
        Mark premium as expired.
        """

        result = await self.collection.update_one(
            {
                "user_id": user_id,
            },
            {
                "$set": {
                    "active": False,
                    "updated_at": self.now(),
                }
            },
        )

        if result.modified_count:
            log.info(
                "Premium expired for %s",
                user_id,
            )

        return result.modified_count > 0

    # --------------------------------------------------
    # Remaining Days
    # --------------------------------------------------

    async def remaining_days(
        self,
        user_id: int,
    ) -> int | None:
        """
        Returns remaining premium days.
        Lifetime returns None.
        """

        premium = await self.get_premium(user_id)

        if premium is None:
            return 0

        expires_at = premium.get("expires_at")

        if expires_at is None:
            return None

        seconds = (expires_at - self.now()).total_seconds()

        if seconds <= 0:
            return 0

        return int(seconds // 86400)

    # --------------------------------------------------
    # Renew Premium
    # --------------------------------------------------

    async def renew(
        self,
        user_id: int,
        days: int,
    ) -> bool:
        """
        Extend an existing premium subscription.
        """

        premium = await self.get_premium(user_id)

        if premium is None:
            return False

        current = premium.get("expires_at")

        if current is None:
            return True

        start = max(current, self.now())

        result = await self.collection.update_one(
            {
                "user_id": user_id,
            },
            {
                "$set": {
                    "expires_at": start + timedelta(days=days),
                    "active": True,
                    "updated_at": self.now(),
                }
            },
        )

        return result.modified_count > 0

    # --------------------------------------------------
    # Badge
    # --------------------------------------------------

    async def badge(
        self,
        user_id: int,
    ) -> str:

        if not await self.is_premium(user_id):
            return ""

        premium = await self.get_premium(user_id)

        plan = premium["plan"]

        badges = {
            "monthly": "⭐",
            "yearly": "🌟",
            "lifetime": "👑",
        }

        return badges.get(plan, "⭐")

    # --------------------------------------------------
    # Features
    # --------------------------------------------------

    async def priority_queue(
        self,
        user_id: int,
    ) -> bool:
        """
        Premium users can use priority queue.
        """

        return await self.is_premium(user_id)

    async def unlimited_queue(
        self,
        user_id: int,
    ) -> bool:

        return await self.is_premium(user_id)

    async def large_files(
        self,
        user_id: int,
    ) -> bool:

        return await self.is_premium(user_id)

    async def fast_upload(
        self,
        user_id: int,
    ) -> bool:

        return await self.is_premium(user_id)

      # --------------------------------------------------
    # Statistics
    # --------------------------------------------------

    async def total_premium_users(self) -> int:
        return await self.collection.count_documents(
            {
                "active": True,
            }
        )

    async def total_expired_users(self) -> int:
        return await self.collection.count_documents(
            {
                "active": False,
            }
        )

    async def total_lifetime_users(self) -> int:
        return await self.collection.count_documents(
            {
                "plan": "lifetime",
                "active": True,
            }
        )

    # --------------------------------------------------
    # Lists
    # --------------------------------------------------

    async def active_users(
        self,
        limit: int = 100,
    ) -> list[dict[str, Any]]:

        cursor = (
            self.collection
            .find(
                {
                    "active": True,
                }
            )
            .sort("updated_at", -1)
            .limit(limit)
        )

        return await cursor.to_list(length=limit)

    async def expired_users(
        self,
        limit: int = 100,
    ) -> list[dict[str, Any]]:

        cursor = (
            self.collection
            .find(
                {
                    "active": False,
                }
            )
            .sort("updated_at", -1)
            .limit(limit)
        )

        return await cursor.to_list(length=limit)

    # --------------------------------------------------
    # Search
    # --------------------------------------------------

    async def find_by_plan(
        self,
        plan: str,
    ) -> list[dict[str, Any]]:

        cursor = self.collection.find(
            {
                "plan": plan,
                "active": True,
            }
        )

        return await cursor.to_list(length=None)

    # --------------------------------------------------
    # Cleanup
    # --------------------------------------------------

    async def cleanup_expired(self) -> int:
        """
        Expire all outdated premium accounts.
        """

        result = await self.collection.update_many(
            {
                "active": True,
                "expires_at": {
                    "$lte": self.now(),
                },
            },
            {
                "$set": {
                    "active": False,
                    "updated_at": self.now(),
                }
            },
        )

        if result.modified_count:
            log.info(
                "Expired %d premium users.",
                result.modified_count,
            )

        return result.modified_count

    # --------------------------------------------------
    # Delete
    # --------------------------------------------------

    async def delete_all(self) -> int:

        result = await self.collection.delete_many({})

        return result.deleted_count

    # --------------------------------------------------
    # Broadcast Helper
    # --------------------------------------------------

    async def premium_user_ids(self):

        async for user in self.collection.find(
            {
                "active": True,
            },
            {
                "_id": 0,
                "user_id": 1,
            },
        ):
            yield user["user_id"]

    # --------------------------------------------------
    # Dashboard Stats
    # --------------------------------------------------

    async def stats(self) -> dict[str, int]:

        return {
            "premium": await self.total_premium_users(),
            "expired": await self.total_expired_users(),
            "lifetime": await self.total_lifetime_users(),
        }


premium_db = PremiumDatabase()
