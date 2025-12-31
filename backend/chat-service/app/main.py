# ============================================================
# Chat Service - FastAPI Application
# ============================================================

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.api.v1 import conversations, chat
from app.services.agent_service import cleanup


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}...")
    await init_db()
    print("Database initialized.")

    yield

    # Shutdown
    print("Shutting down...")
    await cleanup()
    print("Cleanup completed.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Chat Service for Stream-Agent V9 - Handles conversations, messages, and AI agent interactions",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(conversations.router)
app.include_router(chat.router)


@app.get("/")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": "connected",
    }
