"""Task status in-memory cache with DB persistence."""
from __future__ import annotations

import asyncio
from collections.abc import Iterator, MutableMapping
from typing import Any

from moana.config import get_settings
from moana.services.task_status import get_task_status_service


class _TaskStatusProxy(MutableMapping):
    """Mutable mapping proxy for a single task status entry.

    Mutating the proxy writes back to the owning cache and schedules an
    asynchronous persistence update, so call-sites can keep using dict-like
    semantics (`_cache[task_id].update(...)`).
    """

    def __init__(self, cache: "TaskStatusCache", task_id: str):
        self._cache = cache
        self._task_id = task_id

    @property
    def _payload(self) -> dict[str, Any]:
        return self._cache._store[self._task_id]

    def __getitem__(self, key: str) -> Any:
        return self._payload[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._payload[key] = value
        self._cache._flush_async(self._task_id, self._payload)

    def __delitem__(self, key: str) -> None:
        self._payload.pop(key, None)
        self._cache._flush_async(self._task_id, self._payload)

    def __iter__(self) -> Iterator:
        return iter(self._payload)

    def __len__(self) -> int:
        return len(self._payload)

    def get(self, key: str, default: Any = None) -> Any:
        return self._payload.get(key, default)

    def copy(self) -> dict[str, Any]:
        return dict(self._payload)


class TaskStatusCache:
    """In-process task status cache backed by persistent DB rows."""

    def __init__(self, task_type: str):
        self._task_type = task_type
        self._store: dict[str, dict[str, Any]] = {}
        self._service = get_task_status_service()

    def __contains__(self, task_id: str) -> bool:
        return task_id in self._store

    def __getitem__(self, task_id: str) -> _TaskStatusProxy:
        if task_id not in self._store:
            # Avoid silently creating entries on read access.
            raise KeyError(task_id)
        return _TaskStatusProxy(self, task_id)

    def __setitem__(self, task_id: str, payload: dict[str, Any]) -> None:
        self._store[task_id] = dict(payload or {})
        self._flush_async(task_id, self._store[task_id])

    def __len__(self) -> int:
        return len(self._store)

    def values(self) -> list[dict[str, Any]]:
        return [dict(v) for v in self._store.values()]

    async def get(self, task_id: str) -> dict[str, Any] | None:
        """Get a task status by id, fallback to DB on cache miss."""
        cached = self._store.get(task_id)
        if cached is not None:
            return dict(cached)

        db_status = await self._service.get_status(task_id)
        if not db_status or db_status.get("task_type") != self._task_type:
            return None

        self._store[task_id] = dict(db_status)
        return dict(db_status)

    async def list(self, limit: int = 50) -> list[dict[str, Any]]:
        """List latest task statuses from DB by task type."""
        rows = await self._service.list_statuses(task_type=self._task_type, limit=limit)
        self._sync_from_rows(rows)
        return rows

    async def delete(self, task_id: str) -> None:
        """Delete status from both cache and DB."""
        self._store.pop(task_id, None)
        await self._service.delete_status(task_id)

    async def refresh(self, limit: int | None = None) -> None:
        """Refresh cache from DB (for startup / periodic rebuild)."""
        if limit is None:
            settings = get_settings()
            limit = max(50, settings.task_status_max_finished * 2)
        rows = await self._service.list_statuses(task_type=self._task_type, limit=limit)
        self._sync_from_rows(rows)

    async def cleanup(self, ttl_seconds: int | None = None, max_finished: int | None = None) -> int:
        """Cleanup DB statuses and sync cache."""
        deleted = await self._service.cleanup_expired(ttl_seconds=ttl_seconds, max_finished=max_finished)
        if deleted:
            await self.refresh()
        return deleted

    def _sync_from_rows(self, rows: list[dict[str, Any]]) -> None:
        """Replace in-memory cache with latest rows."""
        self._store = {
            row["task_id"]: row
            for row in rows
            if row.get("task_id") is not None and row.get("task_type") == self._task_type
        }

    def _flush_async(self, task_id: str, payload: dict[str, Any]) -> None:
        """Flush one status update asynchronously."""

        async def _flush() -> None:
            await self._service.set_status(task_id=task_id, task_type=self._task_type, **payload)

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return
        loop.create_task(_flush())
