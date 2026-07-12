"""
database/thumbnails.py

Thumbnail database manager.
"""

from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorCollection

from database import db


class ThumbnailDatabase:
    """
    MongoDB manager for user thumbnails.
    """

    COLLECTION = "thumbnails"

    def __init__(self) -> None:

        self.collection: AsyncIOMotorCollection = db[self.COLLECTION]

    # --------------------------------------------------
    # Save
    # --------------------------------------------------

    async def save_thumbnail(
        self,
        user_id: int,
        file_id: str,
        path: str | None = None,
    ) -> None:

        await self.collection.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "file_id": file_id,
                    "path": path,
                }
            },
            upsert=True,
        )

    # --------------------------------------------------
    # Get
    # --------------------------------------------------

    async def get_thumbnail(
        self,
        user_id: int,
    ) -> str | None:

        data = await self.collection.find_one(
            {"user_id": user_id}
        )

        if not data:
            return None

        return data.get("path")

    # --------------------------------------------------
    # Get Telegram File ID
    # --------------------------------------------------

    async def get_file_id(
        self,
        user_id: int,
    ) -> str | None:

        data = await self.collection.find_one(
            {"user_id": user_id}
        )

        if not data:
            return None

        return data.get("file_id")

    # --------------------------------------------------
    # Delete
    # --------------------------------------------------

    async def delete_thumbnail(
        self,
        user_id: int,
    ) -> bool:

        result = await self.collection.delete_one(
            {"user_id": user_id}
        )

        return result.deleted_count > 0

    # --------------------------------------------------
    # Exists
    # --------------------------------------------------

    async def exists(
        self,
        user_id: int,
    ) -> bool:

        return (
            await self.collection.count_documents(
                {"user_id": user_id},
                limit=1,
            )
            > 0
        )

    # --------------------------------------------------
    # Count
    # --------------------------------------------------

    async def count(self) -> int:

        return await self.collection.count_documents({})

    # --------------------------------------------------
    # All Users
    # --------------------------------------------------

    async def all_users(self) -> list[int]:

        users = []

        async for item in self.collection.find(
            {},
            {"user_id": 1},
        ):

            users.append(
                item["user_id"]
            )

        return users


thumbnails_db = ThumbnailDatabase()
