"""
helpers/cleaner.py

Temporary file cleanup helper.
"""

from __future__ import annotations

import asyncio
import shutil
from pathlib import Path

from logger import get_logger

log = get_logger(__name__)


class Cleaner:
    """
    Handles cleanup of temporary files and folders.
    """

    # --------------------------------------------------
    # Delete File
    # --------------------------------------------------

    async def remove_file(
        self,
        file: str | Path,
    ) -> bool:

        file = Path(file)

        try:

            if file.exists():
                file.unlink()

            return True

        except Exception:

            log.exception(
                "Unable to remove file: %s",
                file,
            )

            return False

    # --------------------------------------------------
    # Delete Directory
    # --------------------------------------------------

    async def remove_directory(
        self,
        directory: str | Path,
    ) -> bool:

        directory = Path(directory)

        try:

            if directory.exists():
                shutil.rmtree(directory)

            return True

        except Exception:

            log.exception(
                "Unable to remove directory: %s",
                directory,
            )

            return False

    # --------------------------------------------------
    # Empty Directory
    # --------------------------------------------------

    async def empty_directory(
        self,
        directory: str | Path,
    ) -> None:

        directory = Path(directory)

        if not directory.exists():
            return

        for item in directory.iterdir():

            if item.is_file():

                await self.remove_file(item)

            elif item.is_dir():

                await self.remove_directory(item)

    # --------------------------------------------------
    # Remove Empty Parents
    # --------------------------------------------------

    async def remove_empty_parents(
        self,
        path: str | Path,
        stop: str | Path,
    ) -> None:

        path = Path(path).parent

        stop = Path(stop).resolve()

        while path != stop:

            try:

                path.rmdir()

            except OSError:

                break

            path = path.parent

    # --------------------------------------------------
    # Cleanup Old Files
    # --------------------------------------------------

    async def cleanup_old_files(
        self,
        directory: str | Path,
        max_age: int,
    ) -> int:

        directory = Path(directory)

        if not directory.exists():
            return 0

        removed = 0

        now = asyncio.get_running_loop().time()

        for file in directory.rglob("*"):

            if not file.is_file():
                continue

            try:

                age = now - file.stat().st_mtime

                if age > max_age:

                    file.unlink()

                    removed += 1

            except Exception:

                log.exception(
                    "Failed cleaning %s",
                    file,
                )

        return removed

    # --------------------------------------------------
    # Cleanup User Workspace
    # --------------------------------------------------

    async def cleanup_workspace(
        self,
        workspace: str | Path,
    ) -> None:

        workspace = Path(workspace)

        if not workspace.exists():
            return

        await self.empty_directory(workspace)

        try:

            workspace.rmdir()

        except OSError:

            pass


cleaner = Cleaner()
