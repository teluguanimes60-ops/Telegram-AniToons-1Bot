"""
database/queue.py

Queue Database Manager

Part 1
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pymongo import ASCENDING

from core.database import db
from logger import get_logger

log = get_logger(__name__)


class QueueDatabase:
    """Queue Collection Manager."""

    def __init__(self) -> None:
        self.collection = db.queue

    @staticmethod
    def now() -> datetime:
        return datetime.now(timezone.utc)

    # --------------------------------------------------
    # Indexes
    # --------------------------------------------------

    async def create_indexes(self) -> None:

        await self.collection.create_index(
            [("job_id", ASCENDING)],
            unique=True,
        )

        await self.collection.create_index(
            [("user_id", ASCENDING)],
        )

        await self.collection.create_index(
            [("status", ASCENDING)],
        )

        await self.collection.create_index(
            [("priority", ASCENDING)],
        )

        await self.collection.create_index(
            [("created_at", ASCENDING)],
        )

        log.info("Queue indexes created.")

    # --------------------------------------------------
    # Default Job
    # --------------------------------------------------

    def default_job(
        self,
        job_id: str,
        user_id: int,
        mode: str,
    ) -> dict[str, Any]:

        return {
            "job_id": job_id,
            "user_id": user_id,
            "mode": mode,
            "status": "waiting",
            "priority": 0,
            "progress": 0,
            "current_step": "",
            "filename": "",
            "created_at": self.now(),
            "started_at": None,
            "finished_at": None,
            "paused": False,
            "cancelled": False,
        }

    # --------------------------------------------------
    # Add Job
    # --------------------------------------------------

    async def add_job(
        self,
        job_id: str,
        user_id: int,
        mode: str,
        priority: int = 0,
    ) -> bool:

        if await self.job_exists(job_id):
            return False

        job = self.default_job(
            job_id,
            user_id,
            mode,
        )

        job["priority"] = priority

        await self.collection.insert_one(job)

        log.info(
            "Queue Job Added: %s",
            job_id,
        )

        return True

    # --------------------------------------------------
    # Get Job
    # --------------------------------------------------

    async def get_job(
        self,
        job_id: str,
    ) -> dict[str, Any] | None:

        return await self.collection.find_one(
            {
                "job_id": job_id,
            }
        )

    # --------------------------------------------------
    # Exists
    # --------------------------------------------------

    async def job_exists(
        self,
        job_id: str,
    ) -> bool:

        return (
            await self.collection.count_documents(
                {
                    "job_id": job_id,
                },
                limit=1,
            )
            > 0
        )

    # --------------------------------------------------
    # Update Job
    # --------------------------------------------------

    async def update_job(
        self,
        job_id: str,
        **fields: Any,
    ) -> bool:

        if not fields:
            return False

        result = await self.collection.update_one(
            {
                "job_id": job_id,
            },
            {
                "$set": fields,
            },
        )

        return result.modified_count > 0

    # --------------------------------------------------
    # Delete Job
    # --------------------------------------------------

    async def delete_job(
        self,
        job_id: str,
    ) -> bool:

        result = await self.collection.delete_one(
            {
                "job_id": job_id,
            }
        )

        return result.deleted_count > 0


queue_db = QueueDatabase()

    # --------------------------------------------------
    # Job Status
    # --------------------------------------------------

    async def start_job(
        self,
        job_id: str,
    ) -> bool:

        return await self.update_job(
            job_id,
            status="running",
            started_at=self.now(),
            paused=False,
            cancelled=False,
        )

    async def finish_job(
        self,
        job_id: str,
    ) -> bool:

        return await self.update_job(
            job_id,
            status="completed",
            finished_at=self.now(),
            progress=100,
        )

    async def fail_job(
        self,
        job_id: str,
        error: str,
    ) -> bool:

        return await self.update_job(
            job_id,
            status="failed",
            error=error,
            finished_at=self.now(),
        )

    # --------------------------------------------------
    # Pause / Resume
    # --------------------------------------------------

    async def pause_job(
        self,
        job_id: str,
    ) -> bool:

        return await self.update_job(
            job_id,
            paused=True,
            status="paused",
        )

    async def resume_job(
        self,
        job_id: str,
    ) -> bool:

        return await self.update_job(
            job_id,
            paused=False,
            status="running",
        )

    async def cancel_job(
        self,
        job_id: str,
    ) -> bool:

        return await self.update_job(
            job_id,
            cancelled=True,
            status="cancelled",
            finished_at=self.now(),
        )

    # --------------------------------------------------
    # Progress
    # --------------------------------------------------

    async def set_progress(
        self,
        job_id: str,
        progress: float,
    ) -> bool:

        progress = max(
            0.0,
            min(100.0, progress),
        )

        return await self.update_job(
            job_id,
            progress=round(progress, 2),
        )

    async def get_progress(
        self,
        job_id: str,
    ) -> float:

        job = await self.get_job(job_id)

        if not job:
            return 0.0

        return float(
            job.get("progress", 0),
        )

    # --------------------------------------------------
    # Processing Step
    # --------------------------------------------------

    async def set_step(
        self,
        job_id: str,
        step: str,
    ) -> bool:

        return await self.update_job(
            job_id,
            current_step=step,
        )

    async def get_step(
        self,
        job_id: str,
    ) -> str:

        job = await self.get_job(job_id)

        if not job:
            return ""

        return job.get(
            "current_step",
            "",
        )

    # --------------------------------------------------
    # Filename
    # --------------------------------------------------

    async def set_filename(
        self,
        job_id: str,
        filename: str,
    ) -> bool:

        return await self.update_job(
            job_id,
            filename=filename,
        )

    async def get_filename(
        self,
        job_id: str,
    ) -> str:

        job = await self.get_job(job_id)

        if not job:
            return ""

        return job.get(
            "filename",
            "",
        )

    # --------------------------------------------------
    # Status
    # --------------------------------------------------

    async def get_status(
        self,
        job_id: str,
    ) -> str:

        job = await self.get_job(job_id)

        if not job:
            return "unknown"

        return job.get(
            "status",
            "waiting",
        )

    async def is_running(
        self,
        job_id: str,
    ) -> bool:

        return (
            await self.get_status(job_id)
            == "running"
        )

    async def is_paused(
        self,
        job_id: str,
    ) -> bool:

        job = await self.get_job(job_id)

        if not job:
            return False

        return job.get(
            "paused",
            False,
        )

    async def is_cancelled(
        self,
        job_id: str,
    ) -> bool:

        job = await self.get_job(job_id)

        if not job:
            return False

        return job.get(
            "cancelled",
            False,
        )

          # --------------------------------------------------
    # Waiting Queue
    # --------------------------------------------------

    async def next_waiting_job(
        self,
    ) -> dict[str, Any] | None:
        """
        Return the next waiting job ordered by:
        1. Highest priority
        2. Oldest job
        """

        return await self.collection.find_one(
            {
                "status": "waiting",
                "cancelled": False,
            },
            sort=[
                ("priority", -1),
                ("created_at", 1),
            ],
        )

    async def waiting_jobs(
        self,
    ) -> list[dict[str, Any]]:

        cursor = (
            self.collection
            .find(
                {
                    "status": "waiting",
                    "cancelled": False,
                }
            )
            .sort(
                [
                    ("priority", -1),
                    ("created_at", 1),
                ]
            )
        )

        return await cursor.to_list(length=None)

    # --------------------------------------------------
    # Running Jobs
    # --------------------------------------------------

    async def running_jobs(
        self,
    ) -> list[dict[str, Any]]:

        cursor = self.collection.find(
            {
                "status": "running",
            }
        )

        return await cursor.to_list(length=None)

    async def running_count(self) -> int:

        return await self.collection.count_documents(
            {
                "status": "running",
            }
        )

    # --------------------------------------------------
    # User Queue
    # --------------------------------------------------

    async def user_jobs(
        self,
        user_id: int,
    ) -> list[dict[str, Any]]:

        cursor = (
            self.collection
            .find(
                {
                    "user_id": user_id,
                }
            )
            .sort("created_at", -1)
        )

        return await cursor.to_list(length=None)

    async def active_user_job(
        self,
        user_id: int,
    ) -> dict[str, Any] | None:

        return await self.collection.find_one(
            {
                "user_id": user_id,
                "status": {
                    "$in": [
                        "waiting",
                        "running",
                        "paused",
                    ]
                },
            }
        )

    # --------------------------------------------------
    # Queue Position
    # --------------------------------------------------

    async def queue_position(
        self,
        job_id: str,
    ) -> int:

        waiting = await self.waiting_jobs()

        for index, job in enumerate(waiting, start=1):
            if job["job_id"] == job_id:
                return index

        return 0

    # --------------------------------------------------
    # Statistics
    # --------------------------------------------------

    async def total_jobs(self) -> int:

        return await self.collection.count_documents({})

    async def completed_jobs(self) -> int:

        return await self.collection.count_documents(
            {
                "status": "completed",
            }
        )

    async def failed_jobs(self) -> int:

        return await self.collection.count_documents(
            {
                "status": "failed",
            }
        )

    async def cancelled_jobs(self) -> int:

        return await self.collection.count_documents(
            {
                "status": "cancelled",
            }
        )

    # --------------------------------------------------
    # Cleanup
    # --------------------------------------------------

    async def cleanup_finished_jobs(self) -> int:
        """
        Delete completed, failed and cancelled jobs.
        """

        result = await self.collection.delete_many(
            {
                "status": {
                    "$in": [
                        "completed",
                        "failed",
                        "cancelled",
                    ]
                }
            }
        )

        log.info(
            "Removed %d finished jobs.",
            result.deleted_count,
        )

        return result.deleted_count

    # --------------------------------------------------
    # Crash Recovery
    # --------------------------------------------------

    async def recover_running_jobs(self) -> int:
        """
        After restart, running jobs become waiting jobs.
        """

        result = await self.collection.update_many(
            {
                "status": "running",
            },
            {
                "$set": {
                    "status": "waiting",
                    "paused": False,
                }
            },
        )

        log.info(
            "Recovered %d jobs.",
            result.modified_count,
        )

        return result.modified_count

    # --------------------------------------------------
    # Dashboard
    # --------------------------------------------------

    async def stats(self) -> dict[str, int]:

        return {
            "total": await self.total_jobs(),
            "running": await self.running_count(),
            "waiting": await self.collection.count_documents(
                {
                    "status": "waiting",
                }
            ),
            "completed": await self.completed_jobs(),
            "failed": await self.failed_jobs(),
            "cancelled": await self.cancelled_jobs(),
        }


queue_db = QueueDatabase()
