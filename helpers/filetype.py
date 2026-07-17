"""
helpers/filetype.py

File type detection helper.
"""

from __future__ import annotations

from pathlib import Path


VIDEO_EXTENSIONS = {
    ".mp4",
    ".mkv",
    ".avi",
    ".mov",
    ".webm",
    ".ts",
    ".m4v",
    ".flv",
    ".wmv",
}

AUDIO_EXTENSIONS = {
    ".mp3",
    ".aac",
    ".flac",
    ".ogg",
    ".wav",
    ".m4a",
    ".opus",
}

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp",
    ".gif",
}

DOCUMENT_EXTENSIONS = {
    ".pdf",
    ".epub",
    ".txt",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
}

ARCHIVE_EXTENSIONS = {
    ".zip",
    ".rar",
    ".7z",
    ".tar",
    ".gz",
}

APK_EXTENSIONS = {
    ".apk",
}


class FileType:

    @staticmethod
    def extension(file: str | Path) -> str:
        return Path(file).suffix.lower()

    @classmethod
    def is_video(cls, file: str | Path) -> bool:
        return cls.extension(file) in VIDEO_EXTENSIONS

    @classmethod
    def is_audio(cls, file: str | Path) -> bool:
        return cls.extension(file) in AUDIO_EXTENSIONS

    @classmethod
    def is_image(cls, file: str | Path) -> bool:
        return cls.extension(file) in IMAGE_EXTENSIONS

    @classmethod
    def is_document(cls, file: str | Path) -> bool:
        return cls.extension(file) in DOCUMENT_EXTENSIONS

    @classmethod
    def is_archive(cls, file: str | Path) -> bool:
        return cls.extension(file) in ARCHIVE_EXTENSIONS

    @classmethod
    def is_apk(cls, file: str | Path) -> bool:
        return cls.extension(file) in APK_EXTENSIONS

    @classmethod
    def category(cls, file: str | Path) -> str:

        if cls.is_video(file):
            return "video"

        if cls.is_audio(file):
            return "audio"

        if cls.is_image(file):
            return "image"

        if cls.is_document(file):
            return "document"

        if cls.is_archive(file):
            return "archive"

        if cls.is_apk(file):
            return "apk"

        return "unknown"


filetype = FileType()
