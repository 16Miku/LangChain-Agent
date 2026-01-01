# ============================================================
# RAG Service - Main Entry Point
# ============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.api.v1 import documents, search, ingest


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # Startup
    print(f"Starting {settings.SERVICE_NAME}...")

    # 初始化服务
    from app.services.milvus_service import MilvusService
    from app.services.embedding_service import EmbeddingService

    app.state.milvus_service = MilvusService()
    app.state.embedding_service = EmbeddingService()

    # 确保 Milvus Collection 存在
    try:
        app.state.milvus_service.ensure_collection()
        print(f"Milvus collection '{settings.MILVUS_COLLECTION}' ready")
    except Exception as e:
        print(f"Warning: Failed to connect to Milvus: {e}")
        print("RAG service will start but vector search may not work")

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
    return {"service": settings.SERVICE_NAME, "status": "running"}


@app.get("/health")
async def health_check():
    """健康检查"""
    health = {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "milvus": "unknown",
        "embedding": "ready"
    }

    # 检查 Milvus 连接
    try:
        if hasattr(app.state, 'milvus_service'):
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
