# src/moana/services/storage/cleanup.py
"""Orphan file cleanup service.

Scans local storage and removes files that are no longer referenced
in the database. Designed to be run periodically via cron or manually.

Usage:
    # As CLI
    python -m moana.services.storage.cleanup --dry-run
    python -m moana.services.storage.cleanup --execute

    # Programmatically
    from moana.services.storage.cleanup import OrphanFileCleanup
    cleanup = OrphanFileCleanup()
    result = await cleanup.scan_and_clean(dry_run=True)
"""
import asyncio
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from moana.config import get_settings
from moana.database import async_session_factory
from moana.services.storage.local import LocalStorageService

logger = logging.getLogger(__name__)


@dataclass
class CleanupResult:
    """Result of cleanup operation."""
    scanned_files: int = 0
    referenced_files: int = 0
    orphan_files: int = 0
    deleted_files: int = 0
    deleted_bytes: int = 0
    failed_deletions: int = 0
    dry_run: bool = True
    duration_seconds: float = 0.0
    orphan_file_list: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "scanned_files": self.scanned_files,
            "referenced_files": self.referenced_files,
            "orphan_files": self.orphan_files,
            "deleted_files": self.deleted_files,
            "deleted_bytes": self.deleted_bytes,
            "deleted_mb": round(self.deleted_bytes / (1024 * 1024), 2),
            "failed_deletions": self.failed_deletions,
            "dry_run": self.dry_run,
            "duration_seconds": round(self.duration_seconds, 2),
            "orphan_file_list": self.orphan_file_list[:100],  # Limit to 100 for display
            "errors": self.errors[:20],  # Limit errors
        }


class OrphanFileCleanup:
    """Service to find and clean orphan files from local storage."""

    def __init__(
        self,
        storage_path: Optional[str] = None,
        base_url: Optional[str] = None,
        min_age_hours: int = 24,
    ):
        """Initialize cleanup service.

        Args:
            storage_path: Path to local storage (from config if not specified)
            base_url: Base URL for files (from config if not specified)
            min_age_hours: Only consider files older than this many hours as orphans.
                          This prevents deleting files that are still being generated.
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

        self.min_age_hours = min_age_hours
        self.storage_service = LocalStorageService(
            storage_path=str(self.storage_path),
            base_url=self.base_url,
        )

    def _url_to_key(self, url: str) -> Optional[str]:
        """Convert a full URL to storage key.

        Example:
            https://example.com/media/images/2024/12/18/abc123.jpg
            -> images/2024/12/18/abc123.jpg
        """
        if not url:
            return None

        # Handle both full URLs and relative paths
        if url.startswith(self.base_url):
            return url[len(self.base_url):].lstrip("/")
        elif url.startswith("/media/"):
            return url[7:]  # Remove /media/ prefix
        elif not url.startswith("http"):
            # Already a key or relative path
            return url.lstrip("/")

        return None

    async def _get_referenced_keys_from_db(self) -> set[str]:
        """Extract all referenced file keys from database content_data."""
        referenced_keys = set()

        async with async_session_factory() as db:
            # Query all content_data JSON
            result = await db.execute(
                text("SELECT content_data FROM contents WHERE content_data IS NOT NULL")
            )
            rows = result.fetchall()

            for row in rows:
                content_data = row[0] if row[0] else {}
                keys = self._extract_urls_from_content_data(content_data)
                referenced_keys.update(keys)

            # Also check content_assets table
            result = await db.execute(
                text("SELECT url FROM content_assets WHERE url IS NOT NULL")
            )
            asset_rows = result.fetchall()
            for row in asset_rows:
                key = self._url_to_key(row[0])
                if key:
                    referenced_keys.add(key)

        return referenced_keys

    def _extract_urls_from_content_data(self, content_data: dict) -> set[str]:
        """Recursively extract all URL keys from content_data JSON."""
        keys = set()

        if not isinstance(content_data, dict):
            return keys

        # Known URL fields
        url_fields = [
            "image_url", "audio_url", "video_url",
            "cover_url", "suno_cover_url", "thumbnail_url",
        ]

        for field_name in url_fields:
            url = content_data.get(field_name)
            if url:
                key = self._url_to_key(url)
                if key:
                    keys.add(key)

        # Handle nested structures
        # pages array (picture_book)
        pages = content_data.get("pages", [])
        if isinstance(pages, list):
            for page in pages:
                if isinstance(page, dict):
                    for field_name in url_fields:
                        url = page.get(field_name)
                        if url:
                            key = self._url_to_key(url)
                            if key:
                                keys.add(key)

        # clips array (video)
        clips = content_data.get("clips", [])
        if isinstance(clips, list):
            for clip in clips:
                if isinstance(clip, dict):
                    for field_name in url_fields:
                        url = clip.get(field_name)
                        if url:
                            key = self._url_to_key(url)
                            if key:
                                keys.add(key)

        # all_tracks array (nursery_rhyme)
        all_tracks = content_data.get("all_tracks", [])
        if isinstance(all_tracks, list):
            for track in all_tracks:
                if isinstance(track, dict):
                    for field_name in ["audio_url", "video_url", "cover_url"]:
                        url = track.get(field_name)
                        if url:
                            key = self._url_to_key(url)
                            if key:
                                keys.add(key)

        return keys

    def _get_local_files(self) -> list[tuple[str, int, datetime]]:
        """Scan local storage and return list of (key, size_bytes, mtime)."""
        files = []
        categories = ["images", "audio", "video", "files"]

        for category in categories:
            category_path = self.storage_path / category
            if category_path.exists():
                for file_path in category_path.rglob("*"):
                    if file_path.is_file():
                        try:
                            stat = file_path.stat()
                            # Get relative key
                            key = str(file_path.relative_to(self.storage_path))
                            mtime = datetime.fromtimestamp(stat.st_mtime)
                            files.append((key, stat.st_size, mtime))
                        except Exception as e:
                            logger.warning(f"Error reading file {file_path}: {e}")

        return files

    async def scan_and_clean(
        self,
        dry_run: bool = True,
        min_age_hours: Optional[int] = None,
    ) -> CleanupResult:
        """Scan storage and clean orphan files.

        Args:
            dry_run: If True, only report what would be deleted without actually deleting
            min_age_hours: Override minimum file age (hours) to consider as orphan

        Returns:
            CleanupResult with statistics
        """
        start_time = datetime.now()
        result = CleanupResult(dry_run=dry_run)

        min_age = min_age_hours if min_age_hours is not None else self.min_age_hours
        cutoff_time = datetime.now() - timedelta(hours=min_age)

        try:
            # Step 1: Get all referenced keys from database
            logger.info("Scanning database for referenced files...")
            referenced_keys = await self._get_referenced_keys_from_db()
            result.referenced_files = len(referenced_keys)
            logger.info(f"Found {result.referenced_files} referenced files in database")

            # Step 2: Get all local files
            logger.info("Scanning local storage...")
            local_files = self._get_local_files()
            result.scanned_files = len(local_files)
            logger.info(f"Found {result.scanned_files} files in local storage")

            # Step 3: Find orphans
            orphan_files = []
            for key, size, mtime in local_files:
                if key not in referenced_keys and mtime < cutoff_time:
                    orphan_files.append((key, size))
                    result.orphan_file_list.append(key)

            result.orphan_files = len(orphan_files)
            logger.info(f"Found {result.orphan_files} orphan files (older than {min_age}h)")

            # Step 4: Delete orphans (if not dry run)
            if not dry_run and orphan_files:
                logger.info("Deleting orphan files...")
                for key, size in orphan_files:
                    try:
                        deleted = await self.storage_service.delete_file(key)
                        if deleted:
                            result.deleted_files += 1
                            result.deleted_bytes += size
                        else:
                            result.failed_deletions += 1
                            result.errors.append(f"Failed to delete: {key}")
                    except Exception as e:
                        result.failed_deletions += 1
                        result.errors.append(f"Error deleting {key}: {str(e)}")
            elif dry_run:
                # In dry run, report what would be deleted
                for key, size in orphan_files:
                    result.deleted_bytes += size

        except Exception as e:
            logger.exception(f"Cleanup failed: {e}")
            result.errors.append(f"Cleanup failed: {str(e)}")

        result.duration_seconds = (datetime.now() - start_time).total_seconds()
        return result

    async def get_stats(self) -> dict:
        """Get storage statistics without cleaning."""
        referenced_keys = await self._get_referenced_keys_from_db()
        local_files = self._get_local_files()

        cutoff_time = datetime.now() - timedelta(hours=self.min_age_hours)
        orphan_count = 0
        orphan_size = 0

        for key, size, mtime in local_files:
            if key not in referenced_keys and mtime < cutoff_time:
                orphan_count += 1
                orphan_size += size

        return {
            "total_files": len(local_files),
            "referenced_files": len(referenced_keys),
            "orphan_files": orphan_count,
            "orphan_size_bytes": orphan_size,
            "orphan_size_mb": round(orphan_size / (1024 * 1024), 2),
            "storage_path": str(self.storage_path),
            "min_age_hours": self.min_age_hours,
        }


# CLI entry point
async def main():
    """CLI entry point for cleanup."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Clean orphan files from local storage"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Only report what would be deleted (default)",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually delete orphan files",
    )
    parser.add_argument(
        "--min-age",
        type=int,
        default=24,
        help="Minimum file age in hours to consider as orphan (default: 24)",
    )
    parser.add_argument(
        "--stats-only",
        action="store_true",
        help="Only show statistics, don't clean",
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    cleanup = OrphanFileCleanup(min_age_hours=args.min_age)

    if args.stats_only:
        print("\n📊 Storage Statistics")
        print("=" * 50)
        stats = await cleanup.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        return

    dry_run = not args.execute
    if dry_run:
        print("\n🔍 DRY RUN MODE (no files will be deleted)")
    else:
        print("\n⚠️  EXECUTE MODE (files will be permanently deleted!)")

    print("=" * 50)

    result = await cleanup.scan_and_clean(dry_run=dry_run)

    print(f"\n📊 Cleanup Results")
    print("=" * 50)
    print(f"  Scanned files:     {result.scanned_files}")
    print(f"  Referenced files:  {result.referenced_files}")
    print(f"  Orphan files:      {result.orphan_files}")
    print(f"  Deleted files:     {result.deleted_files}")
    print(f"  Space freed:       {result.deleted_bytes / (1024*1024):.2f} MB")
    print(f"  Failed deletions:  {result.failed_deletions}")
    print(f"  Duration:          {result.duration_seconds:.2f}s")

    if result.orphan_file_list and dry_run:
        print(f"\n📁 Orphan Files (first 20):")
        for f in result.orphan_file_list[:20]:
            print(f"  - {f}")
        if len(result.orphan_file_list) > 20:
            print(f"  ... and {len(result.orphan_file_list) - 20} more")

    if result.errors:
        print(f"\n❌ Errors:")
        for e in result.errors[:10]:
            print(f"  - {e}")


if __name__ == "__main__":
    asyncio.run(main())
