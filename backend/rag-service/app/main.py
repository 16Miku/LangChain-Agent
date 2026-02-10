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


# OpenAPI 标签描述
tags_metadata = [
    {
        "name": "Health",
        "description": "服务健康检查接口",
    },
    {
        "name": "Documents",
        "description": "文档管理接口：列表、详情、删除",
    },
    {
        "name": "Ingest",
        "description": "文档摄取接口：上传文件、摄取文本",
    },
    {
        "name": "Search",
        "description": "检索接口：混合检索、向量检索、BM25 检索、引用追溯",
    },
]

app = FastAPI(
    title="RAG Service",
    description="""
## RAG Service - 检索增强生成服务

Stream-Agent V9 的 RAG 微服务，提供文档解析、向量存储和混合检索功能。

### 功能特性

- **文档解析**: 支持 PDF、TXT、MD、DOCX 格式
- **智能分块**: 语义感知分块、页面感知分块
- **混合检索**: 向量相似度 + BM25 关键词检索
- **重排序**: 基于 Cross-Encoder 的结果重排序
- **引用追溯**: 支持查看引用来源和上下文

### 向量存储后端

| 后端 | 说明 |
|------|------|
| pgvector | PostgreSQL + pgvector 扩展 (推荐) |
| milvus | Milvus 向量数据库 |

### 检索算法

混合检索使用 RRF (Reciprocal Rank Fusion) 算法融合向量和 BM25 结果：

```
score = alpha * vector_score + (1 - alpha) * bm25_score
```

### 认证方式

所有接口都需要在请求头中携带 Bearer Token:

```
Authorization: Bearer <access_token>
```

### 错误码说明

| 状态码 | 说明 |
|--------|------|
| 400 | 请求参数错误 (如不支持的文件类型) |
| 401 | 未认证或令牌无效 |
| 404 | 文档或引用不存在 |
| 500 | 服务器内部错误 |
""",
    version="1.0.0",
    lifespan=lifespan,
    openapi_tags=tags_metadata,
    contact={
        "name": "Stream-Agent Team",
        "email": "support@stream-agent.com",
    },
    license_info={
        "name": "MIT",
    },
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
