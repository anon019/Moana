# src/moana/services/storage/oss.py
from typing import Optional, BinaryIO
from io import BytesIO

from moana.config import get_settings
from moana.services.storage.base import StorageService, StorageResult


class OSSStorageService(StorageService):
    """Aliyun OSS storage service.

    Uses oss2 library for file operations.
    """

    def __init__(self):
        settings = get_settings()
        self.access_key = settings.oss_access_key
        self.secret_key = settings.oss_secret_key
        self.bucket_name = settings.oss_bucket
        self.endpoint = settings.oss_endpoint
        self._bucket = None

    def _get_bucket(self):
        """Get or create OSS bucket connection."""
        if self._bucket is None:
            try:
                import oss2
                auth = oss2.Auth(self.access_key, self.secret_key)
                self._bucket = oss2.Bucket(auth, self.endpoint, self.bucket_name)
            except ImportError:
                return None
            except Exception:
                return None
        return self._bucket

    def _get_public_url(self, key: str) -> str:
        """Generate public URL for a file."""
        if self.endpoint.startswith("http://"):
            endpoint = self.endpoint[7:]
        elif self.endpoint.startswith("https://"):
            endpoint = self.endpoint[8:]
        else:
            endpoint = self.endpoint

        return f"https://{self.bucket_name}.{endpoint}/{key}"

    async def upload_file(
        self,
        file: BinaryIO,
        key: str,
        content_type: Optional[str] = None,
    ) -> StorageResult:
        """Upload a file to OSS."""
        bucket = self._get_bucket()
        if bucket is None:
            return StorageResult(
                success=False,
                error="OSS not configured or oss2 not installed",
            )

        try:
            headers = {}
            if content_type:
                headers["Content-Type"] = content_type

            bucket.put_object(key, file, headers=headers or None)
            url = self._get_public_url(key)

            return StorageResult(
                success=True,
                url=url,
                key=key,
            )
        except Exception as e:
            return StorageResult(
                success=False,
                error=str(e),
            )

    async def upload_bytes(
        self,
        data: bytes,
        key: str,
        content_type: Optional[str] = None,
    ) -> StorageResult:
        """Upload bytes to OSS."""
        return await self.upload_file(BytesIO(data), key, content_type)

    async def download_file(self, key: str) -> Optional[bytes]:
        """Download a file from OSS."""
        bucket = self._get_bucket()
        if bucket is None:
            return None

        try:
            result = bucket.get_object(key)
            return result.read()
        except Exception:
            return None

    async def delete_file(self, key: str) -> bool:
        """Delete a file from OSS."""
        bucket = self._get_bucket()
        if bucket is None:
            return False

        try:
            bucket.delete_object(key)
            return True
        except Exception:
            return False

    async def get_url(self, key: str, expires: int = 3600) -> Optional[str]:
        """Get a signed URL for a file."""
        bucket = self._get_bucket()
        if bucket is None:
            return self._get_public_url(key)

        try:
            url = bucket.sign_url("GET", key, expires)
            return url
        except Exception:
            return self._get_public_url(key)

    async def file_exists(self, key: str) -> bool:
        """Check if a file exists in OSS."""
        bucket = self._get_bucket()
        if bucket is None:
            return False

        try:
            return bucket.object_exists(key)
        except Exception:
            return False
