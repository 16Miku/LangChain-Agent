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

    # 初始化向量存储服务
    # 支持两种后端: milvus 和 pgvector
    app.state.milvus_service = None  # 兼容旧代码

    if settings.VECTOR_STORE_BACKEND == "milvus" and settings.MILVUS_ENABLED:
        # 使用 Milvus 后端
        from app.services.milvus_service import MilvusService
        app.state.milvus_service = MilvusService()
        app.state.vector_service = app.state.milvus_service
        try:
            app.state.milvus_service.ensure_collection()
            print(f"Milvus collection '{settings.MILVUS_COLLECTION}' ready")
        except Exception as e:
            print(f"Warning: Failed to connect to Milvus: {e}")
            app.state.milvus_service = None
            app.state.vector_service = None
    elif settings.VECTOR_STORE_BACKEND == "pgvector" or settings.PGVECTOR_ENABLED:
        # 使用 pgvector 后端 (默认)
        from app.services.pgvector_service import PgvectorService
        app.state.vector_service = PgvectorService()
        try:
            app.state.vector_service.connect()
            stats = app.state.vector_service.get_collection_stats()
            print(f"PgvectorService ready: {stats}")
        except Exception as e:
            print(f"Warning: Failed to initialize PgvectorService: {e}")
            app.state.vector_service = None
    else:
        app.state.vector_service = None
        print("Vector store disabled")

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
        "vector_backend": settings.VECTOR_STORE_BACKEND,
        "milvus_enabled": settings.MILVUS_ENABLED,
        "pgvector_enabled": settings.PGVECTOR_ENABLED,
        "jwt_enabled": settings.JWT_ENABLED
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    health = {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "vector_backend": settings.VECTOR_STORE_BACKEND,
        "vector_store": "unknown",
        "embedding": "ready",
        "database": "sqlite" if "sqlite" in settings.DATABASE_URL else "postgresql"
    }

    # 检查向量服务连接
    if hasattr(app.state, 'vector_service') and app.state.vector_service:
        try:
            if app.state.vector_service.is_connected():
                stats = app.state.vector_service.get_collection_stats()
                health["vector_store"] = "connected"
                health["vector_entities"] = stats.get("num_entities", 0)
                if "backend" in stats:
                    health["vector_backend"] = stats["backend"]
            else:
                health["vector_store"] = "disconnected"
        except Exception as e:
            health["vector_store"] = f"error: {str(e)}"

    return health


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
