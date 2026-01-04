# src/moana/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from moana.config import get_settings
from moana.database import init_db
from moana.api.content import router as content_router
from moana.api.plan import router as plan_router
from moana.api.intent import router as intent_router
from moana.api.play import router as play_router
from moana.api.child import router as child_router
from moana.api.callback import router as callback_router
from moana.api.admin import router as admin_router
# Phase 6 routers
from moana.routers import auth_router, analytics_router, library_router, feedback_router


# API 前缀 - 独立子域名，无需 /kids 前缀
API_PREFIX = "/api/v1"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    settings = get_settings()
    if settings.debug:
        await init_db()
    yield
    # Shutdown
    pass


app = FastAPI(
    title="Kids API (Moana)",
    description="AI-native early childhood education content generation - 早教内容生成系统",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip compression for API responses
app.add_middleware(GZipMiddleware, minimum_size=500)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "project": "kids", "version": "0.1.0"}


# Include routers with /kids prefix
app.include_router(content_router, prefix=f"{API_PREFIX}/content", tags=["content"])
app.include_router(plan_router, prefix=f"{API_PREFIX}/plan", tags=["plan"])
app.include_router(intent_router, prefix=f"{API_PREFIX}/intent", tags=["intent"])
app.include_router(play_router, prefix=f"{API_PREFIX}/play", tags=["play"])
app.include_router(child_router, prefix=f"{API_PREFIX}/child", tags=["child"])
app.include_router(callback_router, prefix=f"{API_PREFIX}/callback", tags=["callback"])
app.include_router(admin_router, prefix=f"{API_PREFIX}/admin", tags=["admin"])
# Phase 6 routers
app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(analytics_router, prefix=API_PREFIX)
app.include_router(library_router, prefix=API_PREFIX)
app.include_router(feedback_router, prefix=API_PREFIX)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
