# src/moana/services/storage/local.py
"""Local file storage service.

Stores files on the local filesystem and serves them via a configured base URL.
Ideal for personal use, development, or single-server deployments.
"""
import os
import hashlib
import aiofiles
import aiofiles.os
from pathlib import Path
from typing import Optional, BinaryIO
from datetime import datetime

from moana.config import get_settings
from moana.services.storage.base import StorageService, StorageResult


class LocalStorageService(StorageService):
    """Local filesystem storage service.

    Files are stored in a configured directory and served via Nginx
    at a configured base URL.

    Directory structure:
        {storage_path}/
        ├── images/
        │   └── 2024/01/15/
        │       └── {hash}.jpg
        ├── audio/
        │   └── 2024/01/15/
        │       └── {hash}.mp3
        └── video/
            └── 2024/01/15/
                └── {hash}.mp4
    """

    def __init__(
        self,
        storage_path: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """Initialize local storage service.

        Args:
            storage_path: Local directory for storing files.
                         Defaults to STORAGE_LOCAL_PATH env var or /var/www/kids/media
            base_url: Base URL for serving files.
                     Defaults to STORAGE_BASE_URL env var or https://example.com/media
        """
        settings = get_settings()

        self.storage_path = Path(
            storage_path
            or getattr(settings, "storage_local_path", None)
            or "/var/www/kids/media"
        )
        self.base_url = (
            base_url
            or getattr(settings, "storage_base_url", None)
            or "https://example.com/media"
        ).rstrip("/")

        # Ensure storage directory exists
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def _get_date_path(self) -> str:
        """Get date-based subdirectory path (YYYY/MM/DD)."""
        now = datetime.now()
        return f"{now.year}/{now.month:02d}/{now.day:02d}"

    def _get_content_hash(self, data: bytes) -> str:
        """Generate a short hash for content deduplication."""
        return hashlib.sha256(data).hexdigest()[:16]

    def _get_extension(self, key: str, content_type: Optional[str]) -> str:
        """Determine file extension from key or content type."""
        # First try to get from the key itself
        if "." in key:
            return key.rsplit(".", 1)[-1].lower()

        # Map content types to extensions
        type_map = {
            "image/jpeg": "jpg",
            "image/jpg": "jpg",
            "image/png": "png",
            "image/webp": "webp",
            "image/gif": "gif",
            "audio/mpeg": "mp3",
            "audio/mp3": "mp3",
            "audio/wav": "wav",
            "audio/ogg": "ogg",
            "video/mp4": "mp4",
            "video/webm": "webm",
        }

        if content_type:
            return type_map.get(content_type.lower(), "bin")

        return "bin"

    def _get_category(self, content_type: Optional[str]) -> str:
        """Determine storage category from content type."""
        if content_type:
            if content_type.startswith("image/"):
                return "images"
            elif content_type.startswith("audio/"):
                return "audio"
            elif content_type.startswith("video/"):
                return "video"
        return "files"

    def _build_storage_key(
        self,
        original_key: str,
        data: bytes,
        content_type: Optional[str],
    ) -> str:
        """Build the final storage key with category/date/hash structure.

        If the original key already has a structured path, use it directly.
        Otherwise, generate a structured path.
        """
        # If key already has directory structure, use it
        if "/" in original_key and not original_key.startswith("temp/"):
            return original_key

        # Generate structured path
        category = self._get_category(content_type)
        date_path = self._get_date_path()
        content_hash = self._get_content_hash(data)
        extension = self._get_extension(original_key, content_type)

        return f"{category}/{date_path}/{content_hash}.{extension}"

    def _get_full_path(self, key: str) -> Path:
        """Get the full filesystem path for a key."""
        return self.storage_path / key

    def _get_public_url(self, key: str) -> str:
        """Generate public URL for a stored file."""
        return f"{self.base_url}/{key}"

    async def upload_file(
        self,
        file: BinaryIO,
        key: str,
        content_type: Optional[str] = None,
    ) -> StorageResult:
        """Upload a file to local storage."""
        try:
            data = file.read()
            return await self.upload_bytes(data, key, content_type)
        except Exception as e:
            return StorageResult(
                success=False,
                error=f"Failed to read file: {str(e)}",
            )

    async def upload_bytes(
        self,
        data: bytes,
        key: str,
        content_type: Optional[str] = None,
    ) -> StorageResult:
        """Upload bytes to local storage."""
        try:
            # Build the final storage key
            final_key = self._build_storage_key(key, data, content_type)
            full_path = self._get_full_path(final_key)

            # Ensure parent directory exists
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file asynchronously
            async with aiofiles.open(full_path, "wb") as f:
                await f.write(data)

            url = self._get_public_url(final_key)

            return StorageResult(
                success=True,
                url=url,
                key=final_key,
            )
        except Exception as e:
            return StorageResult(
                success=False,
                error=f"Failed to save file: {str(e)}",
            )

    async def download_file(self, key: str) -> Optional[bytes]:
        """Download a file from local storage."""
        try:
            full_path = self._get_full_path(key)

            if not full_path.exists():
                return None

            async with aiofiles.open(full_path, "rb") as f:
                return await f.read()
        except Exception:
            return None

    async def delete_file(self, key: str) -> bool:
        """Delete a file from local storage."""
        try:
            full_path = self._get_full_path(key)

            if full_path.exists():
                await aiofiles.os.remove(full_path)

                # Try to remove empty parent directories
                try:
                    parent = full_path.parent
                    while parent != self.storage_path:
                        if not any(parent.iterdir()):
                            parent.rmdir()
                            parent = parent.parent
                        else:
                            break
                except Exception:
                    pass  # Ignore errors when cleaning up empty dirs

                return True
            return False
        except Exception:
            return False

    async def get_url(self, key: str, expires: int = 3600) -> Optional[str]:
        """Get URL for a file.

        Note: Local storage doesn't support signed URLs with expiration.
        The expires parameter is ignored.
        """
        full_path = self._get_full_path(key)
        if full_path.exists():
            return self._get_public_url(key)
        return None

    async def file_exists(self, key: str) -> bool:
        """Check if a file exists in local storage."""
        full_path = self._get_full_path(key)
        return full_path.exists()

    async def get_storage_stats(self) -> dict:
        """Get storage statistics (local storage specific)."""
        try:
            total_size = 0
            file_count = 0
            category_stats = {}

            for category in ["images", "audio", "video", "files"]:
                category_path = self.storage_path / category
                if category_path.exists():
                    cat_size = 0
                    cat_count = 0
                    for file_path in category_path.rglob("*"):
                        if file_path.is_file():
                            cat_size += file_path.stat().st_size
                            cat_count += 1
                    category_stats[category] = {
                        "size_bytes": cat_size,
                        "file_count": cat_count,
                    }
                    total_size += cat_size
                    file_count += cat_count

            return {
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "total_files": file_count,
                "categories": category_stats,
                "storage_path": str(self.storage_path),
            }
        except Exception as e:
            return {"error": str(e)}
