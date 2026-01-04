# src/moana/services/storage/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, BinaryIO


@dataclass
class StorageResult:
    """Result of storage operation."""
    success: bool
    url: Optional[str] = None
    key: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "url": self.url,
            "key": self.key,
            "error": self.error,
        }


class StorageService(ABC):
    """Abstract base class for storage services."""

    @abstractmethod
    async def upload_file(
        self,
        file: BinaryIO,
        key: str,
        content_type: Optional[str] = None,
    ) -> StorageResult:
        """Upload a file to storage.

        Args:
            file: File-like object to upload
            key: Storage key/path for the file
            content_type: MIME type of the file

        Returns:
            StorageResult with URL and status
        """
        pass

    @abstractmethod
    async def upload_bytes(
        self,
        data: bytes,
        key: str,
        content_type: Optional[str] = None,
    ) -> StorageResult:
        """Upload bytes to storage.

        Args:
            data: Bytes to upload
            key: Storage key/path
            content_type: MIME type

        Returns:
            StorageResult with URL and status
        """
        pass

    @abstractmethod
    async def download_file(self, key: str) -> Optional[bytes]:
        """Download a file from storage.

        Args:
            key: Storage key/path

        Returns:
            File bytes or None if not found
        """
        pass

    @abstractmethod
    async def delete_file(self, key: str) -> bool:
        """Delete a file from storage.

        Args:
            key: Storage key/path

        Returns:
            True if deleted, False otherwise
        """
        pass

    @abstractmethod
    async def get_url(self, key: str, expires: int = 3600) -> Optional[str]:
        """Get a signed URL for a file.

        Args:
            key: Storage key/path
            expires: Expiration time in seconds

        Returns:
            Signed URL or None
        """
        pass

    @abstractmethod
    async def file_exists(self, key: str) -> bool:
        """Check if a file exists.

        Args:
            key: Storage key/path

        Returns:
            True if exists, False otherwise
        """
        pass
