# src/moana/routers/__init__.py
from moana.routers.auth import router as auth_router
from moana.routers.analytics import router as analytics_router
from moana.routers.library import router as library_router
from moana.routers.feedback import router as feedback_router

__all__ = ["auth_router", "analytics_router", "library_router", "feedback_router"]
