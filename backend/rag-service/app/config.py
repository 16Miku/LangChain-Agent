# ============================================================
# RAG Service Configuration
# ============================================================

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """RAG Service 配置"""

    # Service
    SERVICE_NAME: str = "rag-service"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/streamagent"

    # Milvus
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    MILVUS_COLLECTION: str = "document_chunks"

    # Embedding
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    # Search
    DEFAULT_TOP_K: int = 10
    DEFAULT_ALPHA: float = 0.5  # 向量检索权重 (1-alpha 为 BM25 权重)
    ENABLE_RERANK: bool = True

    # Reranker
    RERANKER_MODEL: str = "BAAI/bge-reranker-base"

    # MinIO (文件存储)
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "documents"
    MINIO_SECURE: bool = False

    # MinerU API (可选)
    MINERU_API_KEY: str | None = None
    MINERU_API_URL: str = "https://mineru.datadance.cn/api/v1"

    # JWT (用于验证请求)
    JWT_SECRET: str = "your-super-secret-jwt-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
