"""
queue/state.py

Runtime state manager for queue jobs.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field


@dataclass(slots=True)
class JobState:
    """
    Runtime state for a processing job.
    """

    paused: bool = False
    cancelled: bool = False

    progress: float = 0.0

    current_step: str = ""

    pause_event: asyncio.Event = field(default_factory=asyncio.Event)

    lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    def __post_init__(self) -> None:
        self.pause_event.set()


class QueueState:
    """
    Stores runtime state for every active job.
    """

    def __init__(self) -> None:
        self._states: dict[str, JobState] = {}

    # --------------------------------------------------
    # Create
    # --------------------------------------------------

    def create(
        self,
        job_id: str,
    ) -> JobState:

        state = JobState()

        self._states[job_id] = state

        return state

    # --------------------------------------------------
    # Get
    # --------------------------------------------------

    def get(
        self,
        job_id: str,
    ) -> JobState | None:

        return self._states.get(job_id)

    # --------------------------------------------------
    # Remove
    # --------------------------------------------------

    def remove(
        self,
        job_id: str,
    ) -> None:

        self._states.pop(job_id, None)

    # --------------------------------------------------
    # Pause
    # --------------------------------------------------

    def pause(
        self,
        job_id: str,
    ) -> bool:

        state = self.get(job_id)

        if state is None:
            return False

        state.paused = True

        state.pause_event.clear()

        return True

    # --------------------------------------------------
    # Resume
    # --------------------------------------------------

    def resume(
        self,
        job_id: str,
    ) -> bool:

        state = self.get(job_id)

        if state is None:
            return False

        state.paused = False

        state.pause_event.set()

        return True

    # --------------------------------------------------
    # Cancel
    # --------------------------------------------------

    def cancel(
        self,
        job_id: str,
    ) -> bool:

        state = self.get(job_id)

        if state is None:
            return False

        state.cancelled = True

        state.pause_event.set()

        return True

    # --------------------------------------------------
    # Progress
    # --------------------------------------------------

    def set_progress(
        self,
        job_id: str,
        progress: float,
    ) -> None:

        state = self.get(job_id)

        if state is None:
            return

        state.progress = progress

    def get_progress(
        self,
        job_id: str,
    ) -> float:

        state = self.get(job_id)

        if state is None:
            return 0.0

        return state.progress

    # --------------------------------------------------
    # Step
    # --------------------------------------------------

    def set_step(
        self,
        job_id: str,
        step: str,
    ) -> None:

        state = self.get(job_id)

        if state is None:
            return

        state.current_step = step

    def get_step(
        self,
        job_id: str,
    ) -> str:

        state = self.get(job_id)

        if state is None:
            return ""

        return state.current_step

    # --------------------------------------------------
    # Wait
    # --------------------------------------------------

    async def wait_if_paused(
        self,
        job_id: str,
    ) -> None:

        state = self.get(job_id)

        if state is None:
            return

        await state.pause_event.wait()

    # --------------------------------------------------
    # Status
    # --------------------------------------------------

    def is_paused(
        self,
        job_id: str,
    ) -> bool:

        state = self.get(job_id)

        return state.paused if state else False

    def is_cancelled(
        self,
        job_id: str,
    ) -> bool:

        state = self.get(job_id)

        return state.cancelled if state else False


queue_state = QueueState()
