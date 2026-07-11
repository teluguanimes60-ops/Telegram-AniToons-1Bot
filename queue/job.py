"""
queue/job.py

Queue Job Model
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass(slots=True)
class QueueJob:
    """
    Runtime queue job.
    """

    user_id: int

    mode: str

    file_id: str

    filename: str

    priority: int = 0

    metadata: dict[str, Any] = field(default_factory=dict)

    job_id: str = field(
        default_factory=lambda: uuid4().hex
    )

    status: str = "waiting"

    progress: float = 0.0

    current_step: str = ""

    paused: bool = False

    cancelled: bool = False

    created_at: datetime = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )

    started_at: datetime | None = None

    finished_at: datetime | None = None

    error: str | None = None

    # --------------------------------------------------
    # Serialization
    # --------------------------------------------------

    def to_dict(self) -> dict[str, Any]:

        return {
            "job_id": self.job_id,
            "user_id": self.user_id,
            "mode": self.mode,
            "file_id": self.file_id,
            "filename": self.filename,
            "priority": self.priority,
            "metadata": self.metadata,
            "status": self.status,
            "progress": self.progress,
            "current_step": self.current_step,
            "paused": self.paused,
            "cancelled": self.cancelled,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "error": self.error,
        }

    # --------------------------------------------------
    # Deserialize
    # --------------------------------------------------

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "QueueJob":

        return cls(
            job_id=data["job_id"],
            user_id=data["user_id"],
            mode=data["mode"],
            file_id=data["file_id"],
            filename=data["filename"],
            priority=data.get("priority", 0),
            metadata=data.get("metadata", {}),
            status=data.get("status", "waiting"),
            progress=data.get("progress", 0.0),
            current_step=data.get(
                "current_step",
                "",
            ),
            paused=data.get("paused", False),
            cancelled=data.get(
                "cancelled",
                False,
            ),
            created_at=data.get(
                "created_at",
                datetime.now(timezone.utc),
            ),
            started_at=data.get("started_at"),
            finished_at=data.get("finished_at"),
            error=data.get("error"),
        )

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    def start(self) -> None:

        self.status = "running"

        self.started_at = datetime.now(
            timezone.utc
        )

    def finish(self) -> None:

        self.status = "completed"

        self.progress = 100

        self.finished_at = datetime.now(
            timezone.utc
        )

    def fail(
        self,
        error: str,
    ) -> None:

        self.status = "failed"

        self.error = error

        self.finished_at = datetime.now(
            timezone.utc
        )

    def cancel(self) -> None:

        self.cancelled = True

        self.status = "cancelled"

        self.finished_at = datetime.now(
            timezone.utc
        )

    def pause(self) -> None:

        self.paused = True

        self.status = "paused"

    def resume(self) -> None:

        self.paused = False

        self.status = "running"

    def set_progress(
        self,
        progress: float,
    ) -> None:

        self.progress = max(
            0.0,
            min(100.0, progress),
        )

    def set_step(
        self,
        step: str,
    ) -> None:

        self.current_step = step

    @property
    def is_finished(self) -> bool:

        return self.status in {
            "completed",
            "failed",
            "cancelled",
        }

    @property
    def is_running(self) -> bool:

        return self.status == "running"

    @property
    def is_waiting(self) -> bool:

        return self.status == "waiting"

    @property
    def is_paused(self) -> bool:

        return self.paused

    @property
    def is_cancelled(self) -> bool:

        return self.cancelled
