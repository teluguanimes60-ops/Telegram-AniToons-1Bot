"""
queue/manager.py

Runtime Queue Manager

Part 1
"""

from __future__ import annotations

import asyncio
from typing import Awaitable, Callable

from database.queue import queue_db
from database.settings import settings_db
from logger import get_logger

log = get_logger(__name__)

JobHandler = Callable[[str], Awaitable[None]]


class QueueManager:
    """
    Runtime queue manager.

    Controls concurrent jobs while persisting
    queue state in MongoDB.
    """

    def __init__(self) -> None:

        self._workers: set[asyncio.Task] = set()

        self._running_jobs: dict[str, asyncio.Task] = {}

        self._user_jobs: dict[int, str] = {}

        self._handler: JobHandler | None = None

        self._semaphore: asyncio.Semaphore | None = None

        self._running = False

    # --------------------------------------------------
    # Initialize
    # --------------------------------------------------

    async def initialize(self) -> None:

        max_jobs = await settings_db.get_max_active_users()

        self._semaphore = asyncio.Semaphore(max_jobs)

        await queue_db.recover_running_jobs()

        log.info(
            "Queue initialized (%d workers)",
            max_jobs,
        )

    # --------------------------------------------------
    # Job Processor
    # --------------------------------------------------

    def register_handler(
        self,
        handler: JobHandler,
    ) -> None:
        """
        Register the processing function.

        Example:
            queue.register_handler(process_pipeline)
        """

        self._handler = handler

    # --------------------------------------------------
    # Start Manager
    # --------------------------------------------------

    async def start(self) -> None:

        if self._running:
            return

        self._running = True

        asyncio.create_task(
            self._scheduler()
        )

        log.info("Queue manager started.")

    # --------------------------------------------------
    # Stop Manager
    # --------------------------------------------------

    async def stop(self) -> None:

        self._running = False

        for task in list(self._workers):
            task.cancel()

        self._workers.clear()

        self._running_jobs.clear()

        self._user_jobs.clear()

        log.info("Queue manager stopped.")

    # --------------------------------------------------
    # Add Job
    # --------------------------------------------------

    async def add_job(
        self,
        job_id: str,
        user_id: int,
    ) -> bool:

        if user_id in self._user_jobs:
            return False

        self._user_jobs[user_id] = job_id

        return True

      # --------------------------------------------------
# Scheduler
# --------------------------------------------------

    async def _scheduler(self) -> None:
        """
        Continuously schedule waiting jobs while
        free worker slots are available.
        """

        while self._running:

            try:
                if self._semaphore is None:
                    await asyncio.sleep(1)
                    continue

                if self._semaphore.locked():
                    await asyncio.sleep(1)
                    continue

                job = await queue_db.next_waiting_job()

                if job is None:
                    await asyncio.sleep(1)
                    continue

                await self._semaphore.acquire()

                task = asyncio.create_task(
                    self._run_job(job)
                )

                self._workers.add(task)

                task.add_done_callback(
                    self._workers.discard
                )

            except Exception:
                log.exception("Queue scheduler error.")

                await asyncio.sleep(2)

# --------------------------------------------------
# Worker
# --------------------------------------------------

    async def _run_job(
        self,
        job: dict,
    ) -> None:

        job_id = job["job_id"]
        user_id = job["user_id"]

        self._running_jobs[job_id] = asyncio.current_task()

        try:

            await queue_db.start_job(job_id)

            if self._handler is None:
                raise RuntimeError(
                    "Queue handler not registered."
                )

            await self._handler(job_id)

            await queue_db.finish_job(job_id)

        except asyncio.CancelledError:

            await queue_db.cancel_job(job_id)

            raise

        except Exception as e:

            log.exception(
                "Job %s failed.",
                job_id,
            )

            await queue_db.fail_job(
                job_id,
                str(e),
            )

        finally:

            self._running_jobs.pop(
                job_id,
                None,
            )

            self._user_jobs.pop(
                user_id,
                None,
            )

            if self._semaphore:
                self._semaphore.release()

# --------------------------------------------------
# Running Job
# --------------------------------------------------

    def get_running_task(
        self,
        job_id: str,
    ) -> asyncio.Task | None:

        return self._running_jobs.get(job_id)

# --------------------------------------------------
# User Check
# --------------------------------------------------

    def user_busy(
        self,
        user_id: int,
    ) -> bool:

        return user_id in self._user_jobs
