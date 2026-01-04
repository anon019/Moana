# src/moana/services/storage/__init__.py
"""Storage services for media files.

Supports multiple backends:
- local: Local filesystem storage (recommended for personal use)
- oss: Aliyun OSS (for production scale)

Usage:
    from moana.services.storage import get_storage_service

    storage = get_storage_service()
    result = await storage.upload_bytes(data, "image.jpg", "image/jpeg")
    print(result.url)
"""
from moana.services.storage.base import StorageService, StorageResult
from moana.services.storage.local import LocalStorageService
from moana.services.storage.oss import OSSStorageService
from moana.services.storage.cleanup import OrphanFileCleanup, CleanupResult

# Cached storage service instance
_storage_service: StorageService | None = None


def get_storage_service() -> StorageService:
    """Get the configured storage service instance.

    Returns the appropriate storage service based on STORAGE_PROVIDER config:
    - "local": LocalStorageService (default)
    - "oss": OSSStorageService

    The instance is cached for reuse.
    """
    global _storage_service

    if _storage_service is not None:
        return _storage_service

    from moana.config import get_settings

    settings = get_settings()
    provider = settings.storage_provider.lower()

    if provider == "oss":
        _storage_service = OSSStorageService()
    else:
        # Default to local storage
        _storage_service = LocalStorageService()

    return _storage_service


def reset_storage_service() -> None:
    """Reset the cached storage service (useful for testing)."""
    global _storage_service
    _storage_service = None


__all__ = [
    "StorageService",
    "StorageResult",
    "LocalStorageService",
    "OSSStorageService",
    "OrphanFileCleanup",
    "CleanupResult",
    "get_storage_service",
    "reset_storage_service",
]
