"""Task status persistence service."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone, timedelta
from typing import Any, Optional

from sqlalchemy import delete, select

from moana.config import get_settings
from moana.database import async_session_factory
from moana.models.task_status import TaskStatus


def _to_datetime(value: Any) -> Optional[datetime]:
    """Normalize timestamp-like value to datetime."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc)
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            try:
                return datetime.fromtimestamp(float(value), tz=timezone.utc)
            except (TypeError, ValueError):
                return None
    return None


class TaskStatusService:
    """Persisted async task status CRUD."""

    def __init__(self) -> None:
        self._terminal_statuses = {"completed", "failed", "partial", "repair_failed"}

    async def set_status(self, task_id: str, task_type: str = "generic", **payload: Any) -> dict[str, Any]:
        """Upsert a task status entry and return merged payload.

        Supports incremental updates: fields not provided keep previous values.
        """
        payload = dict(payload or {})
        now = datetime.now(timezone.utc)

        async with async_session_factory() as db:
            row = await db.get(TaskStatus, task_id)
            if row is None:
                row = TaskStatus(task_id=task_id, task_type=task_type)
                db.add(row)
                current = {}
            else:
                current = self._to_payload(row)

            if task_type and row.task_type != task_type:
                row.task_type = task_type

            merged = {**current, **payload}
            status = str(merged.get("status") or row.status or "pending")
            merged["status"] = status

            # finished_at 处理：状态从非终态切换为终态时补齐时间戳
            if "finished_at" in payload:
                merged["finished_at"] = _to_datetime(payload.get("finished_at"))
            elif status in self._terminal_statuses and row.status not in self._terminal_statuses:
                merged["finished_at"] = now
            elif status not in self._terminal_statuses:
                merged["finished_at"] = None

            merged.setdefault("progress", row.progress if row is not None else 0)
            merged.setdefault("task_type", row.task_type)
            merged.setdefault("message", row.message)
            merged.setdefault("stage", row.stage)
            merged.setdefault("error", row.error)
            merged.setdefault("content_id", row.content_id)
            merged.setdefault("result", row.result)

            row.status = status
            row.progress = int(merged.get("progress") or 0)
            row.stage = merged.get("stage")
            row.message = merged.get("message")
            row.error = merged.get("error")
            row.content_id = merged.get("content_id")
            row.result = merged.get("result")
            row.payload = {
                k: v
                for k, v in merged.items()
                if k
                not in {
                    "task_id",
                    "task_type",
                    "status",
                    "progress",
                    "stage",
                    "message",
                    "error",
                    "content_id",
                    "result",
                    "finished_at",
                }
            }
            row.finished_at = merged.get("finished_at")

            await db.commit()
            return self._to_payload(row)

    async def _get(self, task_id: str) -> TaskStatus | None:
        async with async_session_factory() as db:
            return await db.get(TaskStatus, task_id)

    async def get_status(self, task_id: str) -> dict[str, Any] | None:
        """Read task status by task_id."""
        row = await self._get(task_id)
        if row is None:
            return None
        return self._to_payload(row)

    async def delete_status(self, task_id: str) -> bool:
        """Delete a task status record."""
        async with async_session_factory() as db:
            result = await db.execute(
                delete(TaskStatus).where(TaskStatus.task_id == task_id)
            )
            await db.commit()
            return (result.rowcount or 0) > 0

    async def list_statuses(self, task_type: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        """List latest task statuses in memory-friendly order."""
        async with async_session_factory() as db:
            statement = select(TaskStatus).order_by(TaskStatus.updated_at.desc())
            if task_type:
                statement = statement.where(TaskStatus.task_type == task_type)
            if limit:
                statement = statement.limit(limit)
            rows = (await db.execute(statement)).scalars().all()
            return [self._to_payload(row) for row in rows]

    async def cleanup_expired(self, ttl_seconds: int | None = None, max_finished: int | None = None) -> int:
        """Clean up terminal tasks by ttl and max retained count."""
        settings = get_settings()
        ttl_seconds = ttl_seconds if ttl_seconds is not None else settings.task_status_ttl_seconds
        max_finished = max_finished if max_finished is not None else settings.task_status_max_finished
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(seconds=ttl_seconds)

        async with async_session_factory() as db:
            terminal = self._terminal_statuses

            deleted = 0
            result = await db.execute(
                delete(TaskStatus)
                .where(
                    TaskStatus.status.in_(terminal),
                    TaskStatus.finished_at.is_not(None),
                    TaskStatus.finished_at < cutoff,
                )
            )
            deleted += int(result.rowcount or 0)

            terminal_rows = (await db.execute(
                select(TaskStatus.task_id)
                .where(TaskStatus.status.in_(terminal))
                .order_by(TaskStatus.finished_at.desc().nullslast())
            )).scalars().all()

            if max_finished is not None and len(terminal_rows) > max_finished:
                drop_ids = terminal_rows[max_finished:]
                result = await db.execute(
                    delete(TaskStatus).where(TaskStatus.task_id.in_(drop_ids))
                )
                deleted += int(result.rowcount or 0)

            await db.commit()
            return deleted

    @staticmethod
    def _to_payload(row: TaskStatus) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "task_id": row.task_id,
            "task_type": row.task_type,
            "status": row.status,
            "progress": row.progress,
            "stage": row.stage,
            "message": row.message,
            "error": row.error,
            "content_id": row.content_id,
            "result": row.result,
            "updated_at": row.updated_at.isoformat() if row.updated_at else None,
        }
        if row.finished_at:
            payload["finished_at"] = row.finished_at.isoformat()
        if row.payload:
            payload.update(row.payload)
        return payload


def schedule_status_update(task_id: str, service: TaskStatusService, **payload: Any) -> None:
    """Schedule fire-and-forget status update."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return

    loop.create_task(service.set_status(task_id=task_id, **payload))


_task_status_service = TaskStatusService()


def get_task_status_service() -> TaskStatusService:
    """Return shared task status service."""
    return _task_status_service
