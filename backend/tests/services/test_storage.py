# tests/services/test_storage.py
import pytest


def test_storage_imports():
    """Test storage service can be imported."""
    from moana.services.storage import (
        StorageService,
        StorageResult,
        OSSStorageService,
    )
    assert StorageService is not None
    assert StorageResult is not None
    assert OSSStorageService is not None


def test_storage_result():
    """Test StorageResult dataclass."""
    from moana.services.storage.base import StorageResult

    result = StorageResult(
        success=True,
        url="https://bucket.oss.example.com/test.png",
        key="test.png",
    )

    assert result.success is True
    assert "test.png" in result.url
    assert result.key == "test.png"
    assert result.error is None

    result_dict = result.to_dict()
    assert result_dict["success"] is True


def test_storage_result_error():
    """Test StorageResult with error."""
    from moana.services.storage.base import StorageResult

    result = StorageResult(
        success=False,
        error="Upload failed",
    )

    assert result.success is False
    assert result.url is None
    assert result.error == "Upload failed"


@pytest.mark.asyncio
async def test_oss_upload_not_configured():
    """Test OSS upload when not configured."""
    from moana.services.storage import OSSStorageService

    service = OSSStorageService()
    result = await service.upload_bytes(b"test data", "test/file.txt")

    # Should fail gracefully when not configured
    assert result.success is False
    assert "not configured" in result.error.lower() or "not installed" in result.error.lower()


@pytest.mark.asyncio
async def test_oss_download_not_configured():
    """Test OSS download when not configured."""
    from moana.services.storage import OSSStorageService

    service = OSSStorageService()
    result = await service.download_file("test/file.txt")

    assert result is None


@pytest.mark.asyncio
async def test_oss_get_url_not_configured():
    """Test OSS get URL when not configured."""
    from moana.services.storage import OSSStorageService

    service = OSSStorageService()
    url = await service.get_url("test/file.txt")

    # Should return public URL format even when not configured
    assert url is not None
    assert "test/file.txt" in url
