# ============================================================
# RAG Service Configuration
# ============================================================

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """RAG Service 配置"""

    # Service
    SERVICE_NAME: str = "rag-service"
    DEBUG: bool = True

    # Database (支持 SQLite 测试模式)
    DATABASE_URL: str = "sqlite:///./rag_test.db"
    # PostgreSQL: "postgresql://postgres:postgres@localhost:5432/streamagent"

    # Milvus (可选)
    MILVUS_ENABLED: bool = False  # 设为 False 可跳过 Milvus
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    MILVUS_COLLECTION: str = "document_chunks"

    # Embedding
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    # Search
    DEFAULT_TOP_K: int = 10
    DEFAULT_ALPHA: float = 0.5  # 向量检索权重 (1-alpha 为 BM25 权重)
    ENABLE_RERANK: bool = True  # 启用 Reranker

    # Reranker
    RERANKER_ENABLED: bool = False  # 是否使用 CrossEncoder (需要下载模型)
    RERANKER_MODEL: str = "BAAI/bge-reranker-base"

    # MinIO (文件存储) - 可选
    MINIO_ENABLED: bool = False
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "documents"
    MINIO_SECURE: bool = False

    # MinerU API (可选)
    MINERU_API_KEY: str | None = None
    MINERU_API_URL: str = "https://mineru.datadance.cn/api/v1"

    # JWT (用于验证请求) - 测试模式可跳过
    JWT_ENABLED: bool = False  # 测试时禁用 JWT 验证
    JWT_SECRET: str = "test-secret-key-for-development"
    JWT_ALGORITHM: str = "HS256"

    # Internal Service Key (用于微服务间调用)
    INTERNAL_SERVICE_KEY: str = "internal-service-key-change-in-production"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
