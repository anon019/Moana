# src/moana/api/admin.py
"""Admin API endpoints for system management.

Includes:
- Storage statistics and cleanup
- System health checks
"""
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from moana.services.storage.cleanup import OrphanFileCleanup, CleanupResult

logger = logging.getLogger(__name__)

router = APIRouter()


# ========== Storage Management ==========

class StorageStatsResponse(BaseModel):
    """Storage statistics response."""
    total_files: int
    referenced_files: int
    orphan_files: int
    orphan_size_bytes: int
    orphan_size_mb: float
    storage_path: str
    min_age_hours: int


class CleanupResponse(BaseModel):
    """Cleanup operation response."""
    scanned_files: int
    referenced_files: int
    orphan_files: int
    deleted_files: int
    deleted_bytes: int
    deleted_mb: float
    failed_deletions: int
    dry_run: bool
    duration_seconds: float
    orphan_file_list: list[str]
    errors: list[str]


@router.get("/storage/stats", response_model=StorageStatsResponse)
async def get_storage_stats(
    min_age_hours: int = Query(24, ge=1, le=720, description="Minimum file age in hours to consider as orphan"),
):
    """Get storage statistics including orphan file count.

    Returns:
    - total_files: Total files in local storage
    - referenced_files: Files referenced in database
    - orphan_files: Files not referenced (potential for cleanup)
    - orphan_size_mb: Size of orphan files in MB
    """
    try:
        cleanup = OrphanFileCleanup(min_age_hours=min_age_hours)
        stats = await cleanup.get_stats()
        return StorageStatsResponse(**stats)
    except Exception as e:
        logger.exception(f"Failed to get storage stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/storage/cleanup", response_model=CleanupResponse)
async def cleanup_storage(
    dry_run: bool = Query(True, description="If true, only report what would be deleted"),
    min_age_hours: int = Query(24, ge=1, le=720, description="Minimum file age in hours to consider as orphan"),
):
    """Clean orphan files from storage.

    Scans local storage for files that are not referenced in the database
    and optionally deletes them.

    **Safety features:**
    - dry_run=true (default): Only reports what would be deleted
    - min_age_hours: Only files older than this are considered orphans
      (prevents deleting files that are still being generated)

    **Example usage:**
    1. First run with dry_run=true to see what would be deleted
    2. Review the orphan_file_list
    3. Run again with dry_run=false to actually delete

    Returns:
    - scanned_files: Total files scanned in storage
    - orphan_files: Files identified as orphans
    - deleted_files: Files actually deleted (0 if dry_run)
    - deleted_mb: Space freed in MB
    """
    try:
        cleanup = OrphanFileCleanup(min_age_hours=min_age_hours)
        result = await cleanup.scan_and_clean(dry_run=dry_run)

        return CleanupResponse(
            scanned_files=result.scanned_files,
            referenced_files=result.referenced_files,
            orphan_files=result.orphan_files,
            deleted_files=result.deleted_files,
            deleted_bytes=result.deleted_bytes,
            deleted_mb=round(result.deleted_bytes / (1024 * 1024), 2),
            failed_deletions=result.failed_deletions,
            dry_run=result.dry_run,
            duration_seconds=round(result.duration_seconds, 2),
            orphan_file_list=result.orphan_file_list[:100],  # Limit for response
            errors=result.errors[:20],
        )
    except Exception as e:
        logger.exception(f"Cleanup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== System Health ==========

@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy"}


@router.get("/providers")
async def get_providers():
    """Get currently configured service providers.

    Returns the active providers for each service type,
    useful for debugging and monitoring.
    """
    from moana.config import get_settings

    settings = get_settings()

    return {
        "llm": settings.llm_provider,
        "image": settings.image_provider,
        "tts": settings.tts_provider,
        "music": settings.music_provider,
        "video": settings.video_provider,
        "storage": settings.storage_provider,
    }
