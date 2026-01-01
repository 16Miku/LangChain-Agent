# ============================================================
# RAG Service - Main Entry Point
# ============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db
from app.api.v1 import documents, search, ingest


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # Startup
    print(f"Starting {settings.SERVICE_NAME}...")
    print(f"Debug mode: {settings.DEBUG}")
    print(f"Database: {settings.DATABASE_URL}")

    # 初始化数据库表
    init_db()
    print("Database tables initialized")

    # 初始化 Embedding 服务
    from app.services.embedding_service import EmbeddingService
    app.state.embedding_service = EmbeddingService()
    print("Embedding service initialized")

    # 初始化 Milvus 服务（可选）
    if settings.MILVUS_ENABLED:
        from app.services.milvus_service import MilvusService
        app.state.milvus_service = MilvusService()
        try:
            app.state.milvus_service.ensure_collection()
            print(f"Milvus collection '{settings.MILVUS_COLLECTION}' ready")
        except Exception as e:
            print(f"Warning: Failed to connect to Milvus: {e}")
            app.state.milvus_service = None
    else:
        app.state.milvus_service = None
        print("Milvus disabled (MILVUS_ENABLED=False)")

    yield

    # Shutdown
    print(f"Shutting down {settings.SERVICE_NAME}...")


app = FastAPI(
    title="RAG Service",
    description="检索增强生成服务 - 支持混合检索、文档解析、引用追溯",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(search.router, prefix="/api/v1/search", tags=["Search"])
app.include_router(ingest.router, prefix="/api/v1/ingest", tags=["Ingest"])


@app.get("/")
async def root():
    return {
        "service": settings.SERVICE_NAME,
        "status": "running",
        "debug": settings.DEBUG,
        "milvus_enabled": settings.MILVUS_ENABLED,
        "jwt_enabled": settings.JWT_ENABLED
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    health = {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "milvus": "disabled" if not settings.MILVUS_ENABLED else "unknown",
        "embedding": "ready",
        "database": "sqlite" if "sqlite" in settings.DATABASE_URL else "postgresql"
    }

    # 检查 Milvus 连接
    if settings.MILVUS_ENABLED and hasattr(app.state, 'milvus_service') and app.state.milvus_service:
        try:
            if app.state.milvus_service.is_connected():
                health["milvus"] = "connected"
            else:
                health["milvus"] = "disconnected"
        except Exception:
            health["milvus"] = "error"

    return health


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
