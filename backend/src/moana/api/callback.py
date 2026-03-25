"""Callback endpoints for external service notifications.

Receives callbacks from Suno and other services to track generation progress.
"""
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Query
from pydantic import BaseModel

from moana.services.task_status_cache import TaskStatusCache

logger = __import__("logging").getLogger(__name__)

router = APIRouter()

# Persisted callback task status caches
_suno_task_status = TaskStatusCache(task_type="suno_callback")
_suno_video_task_status = TaskStatusCache(task_type="suno_video")


class SunoCallbackPayload(BaseModel):
    """Payload from Suno callback."""

    taskId: str | None = None
    status: str | None = None
    sunoData: list[dict] | None = None
    errorMessage: str | None = None

    class Config:
        extra = "allow"  # Allow extra fields from Suno


class TaskStatusResponse(BaseModel):
    """Response for task status query."""

    task_id: str
    status: str
    progress: int
    stage: str | None = None
    error_message: str | None = None
    updated_at: str | None = None
    tracks: list[dict] | None = None
    message: str | None = None


class _SunoStatusMixin:
    def __init__(self, track_fields: bool = False):
        self.progress_map = {
            "PENDING": 10,
            "TEXT_SUCCESS": 30,
            "FIRST_SUCCESS": 60,
            "SUCCESS": 100,
            "SENSITIVE_WORD_ERROR": 100,
            "CREATE_TASK_FAILED": 100,
            "GENERATE_AUDIO_FAILED": 100,
            "CALLBACK_EXCEPTION": 100,
        }
        self.stage_map = {
            "PENDING": "initializing",
            "TEXT_SUCCESS": "lyrics_generated",
            "FIRST_SUCCESS": "first_track_ready",
            "SUCCESS": "complete",
            "SENSITIVE_WORD_ERROR": "error",
            "CREATE_TASK_FAILED": "error",
            "GENERATE_AUDIO_FAILED": "error",
            "CALLBACK_EXCEPTION": "error",
        }
        self.track_fields = track_fields

    def build_status(self, payload: SunoCallbackPayload, task_id: str) -> dict[str, Any]:
        status = (payload.status or "UNKNOWN").upper()
        base = {
            "task_id": task_id,
            "status": status,
            "progress": self.progress_map.get(status, 20),
            "stage": self.stage_map.get(status, "processing"),
            "message": status,
            "error": payload.errorMessage,
            "error_message": payload.errorMessage,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        if self.track_fields and payload.sunoData:
            base["tracks"] = [
                {
                    "id": track.get("id", ""),
                    "title": track.get("title", ""),
                    "audio_url": track.get("audioUrl", "") or track.get("audio_url", ""),
                    "cover_url": track.get("imageUrl", "") or track.get("image_url", ""),
                    "duration": track.get("duration", 0),
                }
                for track in payload.sunoData
            ]
        return base


_suno_mixin = _SunoStatusMixin(track_fields=True)
_suno_video_mixin = _SunoStatusMixin(track_fields=False)


@router.post("/suno")
async def suno_callback(
    payload: SunoCallbackPayload,
    task_id: str = Query(None, description="Task ID from query parameter"),
):
    """Receive callback from Suno API.

    Suno sends callbacks at these stages:
    - TEXT_SUCCESS: Lyrics generated
    - FIRST_SUCCESS: First song completed
    - SUCCESS: All songs completed
    - Error states: SENSITIVE_WORD_ERROR, CREATE_TASK_FAILED, etc.
    """
    # Use task_id from query param or payload
    effective_task_id = task_id or payload.taskId
    if not effective_task_id:
        logger.warning("Suno callback received without task_id")
        return {"status": "error", "message": "No task_id provided"}

    status_payload = _suno_mixin.build_status(payload, effective_task_id)
    _suno_task_status[effective_task_id] = status_payload

    logger.info(
        "Suno callback: task_id=%s, status=%s",
        effective_task_id,
        status_payload.get("status"),
    )

    return {"status": "ok", "received": status_payload.get("status")}


@router.get("/suno/status/{task_id}")
async def get_suno_task_status(task_id: str) -> TaskStatusResponse:
    """Get status of a Suno generation task.

    Frontend can poll this endpoint to show progress.
    """
    data = await _suno_task_status.get(task_id)
    if not data:
        return TaskStatusResponse(
            task_id=task_id,
            status="PENDING",
            progress=5,
            stage="waiting",
            error_message=None,
        )

    return TaskStatusResponse(
        task_id=task_id,
        status=data.get("status", "unknown"),
        progress=int(data.get("progress", 0) or 0),
        stage=data.get("stage"),
        error_message=data.get("error") or data.get("error_message"),
        updated_at=data.get("updated_at"),
        tracks=data.get("tracks"),
        message=data.get("message"),
    )


@router.delete("/suno/status/{task_id}")
async def clear_task_status(task_id: str):
    """Clear task status after frontend has retrieved final result.

    Helps prevent DB growth from accumulated task statuses.
    """
    before = await _suno_task_status.get(task_id)
    await _suno_task_status.delete(task_id)
    return {"status": "ok", "message": "Task status cleared" if before else "Task not found"}


@router.get("/suno/tasks")
async def list_task_statuses(limit: int = 50):
    """List recent task statuses (for debugging)."""
    tasks = await _suno_task_status.list(limit=limit)
    tasks.sort(key=lambda x: x.get("updated_at", "") or "", reverse=True)
    return {"tasks": tasks[:limit], "total": len(tasks)}


# ========== Video Callback ==========


class SunoVideoCallbackPayload(BaseModel):
    """Payload from Suno video callback."""

    taskId: str | None = None
    status: str | None = None
    videoUrl: str | None = None
    errorMessage: str | None = None

    class Config:
        extra = "allow"


@router.post("/suno/video")
async def suno_video_callback(
    payload: SunoVideoCallbackPayload,
    task_id: str = Query(None, description="Task ID from query parameter"),
):
    """Receive callback from Suno video generation API."""
    effective_task_id = task_id or payload.taskId
    if not effective_task_id:
        logger.warning("Suno video callback received without task_id")
        return {"status": "error", "message": "No task_id provided"}

    status = (payload.status or "UNKNOWN").upper()
    _suno_video_task_status[effective_task_id] = {
        "task_id": effective_task_id,
        "status": status,
        "progress": _suno_video_mixin.progress_map.get(status, 20),
        "stage": _suno_video_mixin.stage_map.get(status, "processing"),
        "message": status,
        "video_url": payload.videoUrl or "",
        "error": payload.errorMessage,
        "error_message": payload.errorMessage,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    logger.info(
        "Suno video callback: task_id=%s status=%s video_url=%s",
        effective_task_id,
        status,
        (payload.videoUrl[:50] + "...") if payload.videoUrl else "N/A",
    )

    return {"status": "ok", "received": status}


@router.get("/suno/video/status/{task_id}")
async def get_suno_video_status(task_id: str):
    """Get status of a Suno video generation task."""
    data = await _suno_video_task_status.get(task_id)
    if not data:
        return {
            "task_id": task_id,
            "status": "PENDING",
            "progress": 5,
            "stage": "waiting",
            "video_url": "",
            "error_message": None,
        }

    return {
        "task_id": task_id,
        "status": data.get("status", "unknown"),
        "progress": int(data.get("progress", 0) or 0),
        "stage": data.get("stage"),
        "video_url": data.get("video_url", ""),
        "message": data.get("message"),
        "error_message": data.get("error") or data.get("error_message"),
        "updated_at": data.get("updated_at"),
    }
