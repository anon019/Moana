"""Callback endpoints for external service notifications.

Receives callbacks from Suno and other services to track generation progress.
"""
import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Query
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory task status storage (use Redis in production for persistence)
_task_status: dict[str, dict[str, Any]] = {}


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

    status = payload.status or "UNKNOWN"
    logger.info(f"Suno callback: task_id={effective_task_id}, status={status}")

    # Map Suno status to progress
    progress_map = {
        "PENDING": 10,
        "TEXT_SUCCESS": 30,
        "FIRST_SUCCESS": 60,
        "SUCCESS": 100,
        "SENSITIVE_WORD_ERROR": 100,
        "CREATE_TASK_FAILED": 100,
        "GENERATE_AUDIO_FAILED": 100,
        "CALLBACK_EXCEPTION": 100,
    }

    stage_map = {
        "PENDING": "initializing",
        "TEXT_SUCCESS": "lyrics_generated",
        "FIRST_SUCCESS": "first_track_ready",
        "SUCCESS": "complete",
        "SENSITIVE_WORD_ERROR": "error",
        "CREATE_TASK_FAILED": "error",
        "GENERATE_AUDIO_FAILED": "error",
        "CALLBACK_EXCEPTION": "error",
    }

    # Extract track info if available
    tracks = None
    if payload.sunoData:
        tracks = [
            {
                "id": track.get("id", ""),
                "title": track.get("title", ""),
                "audio_url": track.get("audioUrl", "") or track.get("audio_url", ""),
                "cover_url": track.get("imageUrl", "") or track.get("image_url", ""),
                "duration": track.get("duration", 0),
            }
            for track in payload.sunoData
        ]
        logger.info(f"  Tracks received: {len(tracks)}")

    # Store status
    _task_status[effective_task_id] = {
        "task_id": effective_task_id,
        "status": status,
        "progress": progress_map.get(status, 20),
        "stage": stage_map.get(status, "processing"),
        "error_message": payload.errorMessage,
        "updated_at": datetime.now().isoformat(),
        "tracks": tracks,
    }

    return {"status": "ok", "received": status}


@router.get("/suno/status/{task_id}")
async def get_suno_task_status(task_id: str) -> TaskStatusResponse:
    """Get status of a Suno generation task.

    Frontend can poll this endpoint to show progress.
    """
    if task_id in _task_status:
        data = _task_status[task_id]
        return TaskStatusResponse(**data)

    # Task not found - might not have received callback yet
    return TaskStatusResponse(
        task_id=task_id,
        status="PENDING",
        progress=5,
        stage="waiting",
        error_message=None,
    )


@router.delete("/suno/status/{task_id}")
async def clear_task_status(task_id: str):
    """Clear task status after frontend has retrieved final result.

    Helps prevent memory leak from accumulated task statuses.
    """
    if task_id in _task_status:
        del _task_status[task_id]
        return {"status": "ok", "message": "Task status cleared"}
    return {"status": "ok", "message": "Task not found"}


@router.get("/suno/tasks")
async def list_task_statuses(limit: int = 50):
    """List recent task statuses (for debugging).

    Returns most recent tasks first.
    """
    tasks = list(_task_status.values())
    # Sort by updated_at descending
    tasks.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    return {"tasks": tasks[:limit], "total": len(_task_status)}


# ========== Video Callback ==========

class SunoVideoCallbackPayload(BaseModel):
    """Payload from Suno video callback."""
    taskId: str | None = None
    status: str | None = None
    videoUrl: str | None = None
    errorMessage: str | None = None

    class Config:
        extra = "allow"


# Video task status storage
_video_task_status: dict[str, dict[str, Any]] = {}


@router.post("/suno/video")
async def suno_video_callback(
    payload: SunoVideoCallbackPayload,
    task_id: str = Query(None, description="Task ID from query parameter"),
):
    """Receive callback from Suno video generation API.

    Suno sends callbacks when video generation completes or fails.
    """
    effective_task_id = task_id or payload.taskId
    if not effective_task_id:
        logger.warning("Suno video callback received without task_id")
        return {"status": "error", "message": "No task_id provided"}

    status = payload.status or "UNKNOWN"
    video_url = payload.videoUrl or ""
    logger.info(f"Suno video callback: task_id={effective_task_id}, status={status}, video_url={video_url[:50] if video_url else 'N/A'}")

    _video_task_status[effective_task_id] = {
        "task_id": effective_task_id,
        "status": status,
        "video_url": video_url,
        "error_message": payload.errorMessage,
        "updated_at": datetime.now().isoformat(),
    }

    return {"status": "ok", "received": status}


@router.get("/suno/video/status/{task_id}")
async def get_suno_video_status(task_id: str):
    """Get status of a Suno video generation task."""
    if task_id in _video_task_status:
        return _video_task_status[task_id]

    return {
        "task_id": task_id,
        "status": "PENDING",
        "video_url": "",
        "error_message": None,
    }
