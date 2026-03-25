# src/moana/services/storage/local.py
"""Local file storage service.

Stores files on the local filesystem and serves them via a configured base URL.
Ideal for personal use, development, or single-server deployments.
"""

import asyncio
import hashlib
import inspect
import uuid
from datetime import datetime
from io import BytesIO
from pathlib import Path, PurePosixPath
from typing import Optional, BinaryIO

import aiofiles
import aiofiles.os

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

    _CHUNK_SIZE = 1024 * 1024

    def __init__(
        self,
        storage_path: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        settings = get_settings()

        self.storage_path = Path(
            storage_path
            or getattr(settings, "storage_local_path", None)
            or "/var/www/kids/media"
        )
        self.base_url = (
            base_url
            or getattr(settings, "storage_base_url", None)
            or "https://kids.jackverse.cn/media"
        ).rstrip("/")

        self.storage_path.mkdir(parents=True, exist_ok=True)

    def _get_date_path(self) -> str:
        """Get date-based subdirectory path (YYYY/MM/DD)."""
        now = datetime.now()
        return f"{now.year}/{now.month:02d}/{now.day:02d}"

    @staticmethod
    def _normalize_key(key: str) -> str:
        """Normalize a storage key and harden against path traversal."""
        if not key:
            return ""

        key = key.replace("\\", "/").lstrip("/")
        if "/../" in f"/{key}" or key.startswith("../"):
            raise ValueError("Invalid key path")

        normalized = str(PurePosixPath(key))
        if normalized.startswith("../") or "/../" in f"/{normalized}":
            raise ValueError("Invalid key path")

        return normalized

    def _get_extension(self, key: str, content_type: Optional[str]) -> str:
        """Determine file extension from key or content type."""
        clean_key = key.split("?", 1)[0]
        suffix = PurePosixPath(clean_key).suffix
        if suffix:
            return suffix[1:].lower() or "bin"

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
            if content_type.startswith("audio/"):
                return "audio"
            if content_type.startswith("video/"):
                return "video"

        return "files"

    def _build_storage_key(self, original_key: str, data: bytes, content_type: Optional[str]) -> str:
        """Build the final storage key with category/date/hash structure."""
        if "/" in original_key and not original_key.startswith("temp/"):
            return self._normalize_key(original_key)

        category = self._get_category(content_type)
        date_path = self._get_date_path()
        content_hash = hashlib.sha256(data).hexdigest()[:16]
        extension = self._get_extension(original_key, content_type)
        return f"{category}/{date_path}/{content_hash}.{extension}"

    def _build_storage_key_from_hash(
        self,
        original_key: str,
        content_hash: str,
        content_type: Optional[str],
    ) -> str:
        if "/" in original_key and not original_key.startswith("temp/"):
            return self._normalize_key(original_key)

        category = self._get_category(content_type)
        date_path = self._get_date_path()
        extension = self._get_extension(original_key, content_type)
        return f"{category}/{date_path}/{content_hash}.{extension}"

    def _get_full_path(self, key: str) -> Path:
        return self.storage_path / self._normalize_key(key)

    def _get_public_url(self, key: str) -> str:
        return f"{self.base_url}/{key}"

    async def _read_file_chunk(self, file: BinaryIO) -> bytes:
        """Read a file chunk from sync or async file-like objects."""
        reader = getattr(file, "read", None)
        if not callable(reader):
            return b""

        result = reader(self._CHUNK_SIZE)
        if inspect.isawaitable(result):
            chunk = await result
        else:
            chunk = await asyncio.to_thread(reader, self._CHUNK_SIZE)

        if chunk is None:
            return b""

        if isinstance(chunk, memoryview):
            return chunk.tobytes()

        if isinstance(chunk, bytes):
            return chunk

        if isinstance(chunk, bytearray):
            return bytes(chunk)

        return bytes(chunk)

    async def upload_file(
        self,
        file: BytesIO,
        key: str,
        content_type: Optional[str] = None,
    ) -> StorageResult:
        """Upload a file to local storage using streaming."""
        use_direct_key = "/" in key and not key.startswith("temp/")

        try:
            if use_direct_key:
                final_key = self._normalize_key(key)
                final_path = self._get_full_path(final_key)
                final_path.parent.mkdir(parents=True, exist_ok=True)
                hasher = None
            else:
                hasher = hashlib.sha256()
                final_key = ""
                final_path = self.storage_path / f".upload/{uuid.uuid4().hex}"
                final_path.parent.mkdir(parents=True, exist_ok=True)

            async with aiofiles.open(final_path, "wb") as f:
                while True:
                    chunk = await self._read_file_chunk(file)
                    if not chunk:
                        break

                    if hasher is not None:
                        hasher.update(chunk)

                    await f.write(chunk)

            if hasher is None:
                return StorageResult(
                    success=True,
                    url=self._get_public_url(final_key),
                    key=final_key,
                )

            content_hash = hasher.hexdigest()[:16]
            final_key = self._build_storage_key_from_hash(
                original_key=key,
                content_hash=content_hash,
                content_type=content_type,
            )
            result_path = self._get_full_path(final_key)
            result_path.parent.mkdir(parents=True, exist_ok=True)

            # Duplicate file uploaded before -> keep first file and reuse reference.
            if result_path.exists():
                await aiofiles.os.remove(str(final_path))
                return StorageResult(
                    success=True,
                    url=self._get_public_url(final_key),
                    key=final_key,
                )

            final_path.replace(result_path)
            return StorageResult(
                success=True,
                url=self._get_public_url(final_key),
                key=final_key,
            )
        except Exception as e:
            try:
                if final_path.exists():
                    await aiofiles.os.remove(str(final_path))
            except Exception:
                pass

            return StorageResult(
                success=False,
                error=f"Failed to upload file: {str(e)}",
            )

    async def upload_bytes(
        self,
        data: bytes,
        key: str,
        content_type: Optional[str] = None,
    ) -> StorageResult:
        """Upload bytes to local storage."""
        try:
            final_key = self._build_storage_key(key, data, content_type)
            final_path = self._get_full_path(final_key)
            final_path.parent.mkdir(parents=True, exist_ok=True)

            async with aiofiles.open(final_path, "wb") as f:
                # Write in chunks to avoid large peak memory spikes.
                for i in range(0, len(data), self._CHUNK_SIZE):
                    await f.write(data[i:i + self._CHUNK_SIZE])

            url = self._get_public_url(final_key)
            return StorageResult(success=True, url=url, key=final_key)
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

            if not full_path.exists():
                return False

            await aiofiles.os.remove(str(full_path))

            parent = full_path.parent
            while parent != self.storage_path:
                try:
                    if any(parent.iterdir()):
                        break

                    parent.rmdir()
                    parent = parent.parent
                except Exception:
                    break

            return True
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

            if not self.storage_path.exists():
                return {
                    "total_size_bytes": 0,
                    "total_size_mb": 0,
                    "total_files": 0,
                    "categories": {},
                    "storage_path": str(self.storage_path),
                }

            for file_path in self.storage_path.rglob("*"):
                if not file_path.is_file():
                    continue

                try:
                    stat = file_path.stat()
                except OSError:
                    continue

                rel = file_path.relative_to(self.storage_path)
                category = rel.parts[0] if rel.parts else ""

                if category not in category_stats:
                    category_stats[category] = {
                        "size_bytes": 0,
                        "file_count": 0,
                    }

                category_stats[category]["size_bytes"] += stat.st_size
                category_stats[category]["file_count"] += 1
                total_size += stat.st_size
                file_count += 1

            return {
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "total_files": file_count,
                "categories": category_stats,
                "storage_path": str(self.storage_path),
            }
        except Exception as e:
            return {"error": str(e)}
