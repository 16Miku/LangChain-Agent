# ============================================================
# PgvectorService - PostgreSQL + pgvector 向量数据库服务
# ============================================================
# 使用 pgvector 扩展替代 Milvus，简化部署架构
# 适用于 Supabase / Render 云部署场景
# ============================================================

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json
import numpy as np
from sqlalchemy import create_engine, text, Column, String, Integer, Text, JSON
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

from app.config import settings

# 复用 milvus_service 中的数据类
from app.services.milvus_service import ChunkData, VectorSearchResult


Base = declarative_base()


class PgvectorService:
    """
    PostgreSQL + pgvector 向量数据库服务

    使用 pgvector 扩展进行向量相似度搜索，作为 MilvusService 的替代方案。
    支持两种模式：
    1. PostgreSQL + pgvector: 完整向量搜索功能
    2. SQLite (测试模式): 降级为暴力搜索，用于本地开发测试

    接口与 MilvusService 保持一致，可无缝切换。
    """

    def __init__(self, database_url: str = None):
        """
        初始化 PgvectorService

        Args:
            database_url: 数据库连接 URL，默认使用 settings.DATABASE_URL
        """
        self.database_url = database_url or settings.DATABASE_URL
        self.dimension = settings.EMBEDDING_DIMENSION
        self._engine = None
        self._session_factory = None
        self._is_postgres = "postgresql" in self.database_url.lower()
        self._is_sqlite = "sqlite" in self.database_url.lower()
        self._pgvector_enabled = False
        self._connected = False

    def connect(self) -> bool:
        """连接到数据库并初始化 pgvector"""
        try:
            # 创建引擎
            connect_args = {}
            if self._is_sqlite:
                connect_args["check_same_thread"] = False

            self._engine = create_engine(
                self.database_url,
                connect_args=connect_args,
                echo=False
            )
            self._session_factory = sessionmaker(bind=self._engine)

            # 测试连接
            with self._engine.connect() as conn:
                if self._is_postgres:
                    # PostgreSQL: 尝试启用 pgvector 扩展
                    try:
                        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                        conn.commit()
                        self._pgvector_enabled = True
                        print("pgvector 扩展已启用")
                    except Exception as e:
                        print(f"警告: 无法启用 pgvector 扩展: {e}")
                        print("将使用降级的暴力搜索模式")
                        self._pgvector_enabled = False
                else:
                    # SQLite: 使用降级模式
                    print("SQLite 模式: 向量搜索将使用暴力搜索 (仅用于测试)")
                    self._pgvector_enabled = False

            # 确保向量表存在
            self._ensure_vector_table()

            self._connected = True
            print(f"PgvectorService 已连接到数据库")
            return True

        except Exception as e:
            print(f"连接数据库失败: {e}")
            self._connected = False
            return False

    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self._connected

    def _ensure_vector_table(self):
        """确保向量表存在"""
        with self._engine.connect() as conn:
            if self._is_postgres and self._pgvector_enabled:
                # PostgreSQL + pgvector: 使用 vector 类型
                conn.execute(text(f"""
                    CREATE TABLE IF NOT EXISTS document_embeddings (
                        id VARCHAR(36) PRIMARY KEY,
                        document_id VARCHAR(36) NOT NULL,
                        user_id VARCHAR(36) NOT NULL,
                        chunk_index INTEGER NOT NULL,
                        content TEXT NOT NULL,
                        page_number INTEGER,
                        embedding vector({self.dimension}),
                        metadata JSONB DEFAULT '{{}}'::jsonb,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """))

                # 创建索引
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_embeddings_user_id
                    ON document_embeddings(user_id)
                """))
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_embeddings_document_id
                    ON document_embeddings(document_id)
                """))

                # 创建向量索引 (HNSW)
                try:
                    conn.execute(text("""
                        CREATE INDEX IF NOT EXISTS idx_embeddings_vector
                        ON document_embeddings
                        USING hnsw (embedding vector_cosine_ops)
                        WITH (m = 16, ef_construction = 64)
                    """))
                except Exception as e:
                    print(f"创建 HNSW 索引失败 (可能已存在): {e}")

            else:
                # SQLite / PostgreSQL (无 pgvector): 使用 TEXT 存储 JSON 编码的向量
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS document_embeddings (
                        id VARCHAR(36) PRIMARY KEY,
                        document_id VARCHAR(36) NOT NULL,
                        user_id VARCHAR(36) NOT NULL,
                        chunk_index INTEGER NOT NULL,
                        content TEXT NOT NULL,
                        page_number INTEGER,
                        embedding TEXT,
                        metadata TEXT DEFAULT '{}',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))

                # 创建索引
                try:
                    conn.execute(text("""
                        CREATE INDEX IF NOT EXISTS idx_embeddings_user_id
                        ON document_embeddings(user_id)
                    """))
                    conn.execute(text("""
                        CREATE INDEX IF NOT EXISTS idx_embeddings_document_id
                        ON document_embeddings(document_id)
                    """))
                except Exception:
                    pass  # SQLite 索引可能已存在

            conn.commit()

    def insert(self, chunks: List[ChunkData]) -> List[str]:
        """
        批量插入分块数据

        Args:
            chunks: 分块数据列表

        Returns:
            插入的 ID 列表
        """
        if not self._connected:
            self.connect()

        inserted_ids = []

        with self._engine.connect() as conn:
            for chunk in chunks:
                if self._is_postgres and self._pgvector_enabled:
                    # PostgreSQL + pgvector: 使用原生 vector 类型
                    embedding_str = f"[{','.join(map(str, chunk.embedding))}]"
                    metadata_json = json.dumps(chunk.metadata, ensure_ascii=False)

                    conn.execute(text("""
                        INSERT INTO document_embeddings
                        (id, document_id, user_id, chunk_index, content, page_number, embedding, metadata)
                        VALUES (:id, :doc_id, :user_id, :idx, :content, :page, :embedding::vector, :meta::jsonb)
                        ON CONFLICT (id) DO UPDATE SET
                            content = EXCLUDED.content,
                            embedding = EXCLUDED.embedding,
                            metadata = EXCLUDED.metadata
                    """), {
                        "id": chunk.id,
                        "doc_id": chunk.document_id,
                        "user_id": chunk.user_id,
                        "idx": chunk.chunk_index,
                        "content": chunk.content,
                        "page": chunk.page_number or -1,
                        "embedding": embedding_str,
                        "meta": metadata_json
                    })

                else:
                    # SQLite / 降级模式: 使用 JSON 编码的向量
                    embedding_json = json.dumps(chunk.embedding)
                    metadata_json = json.dumps(chunk.metadata, ensure_ascii=False)

                    # SQLite 使用 INSERT OR REPLACE
                    conn.execute(text("""
                        INSERT OR REPLACE INTO document_embeddings
                        (id, document_id, user_id, chunk_index, content, page_number, embedding, metadata)
                        VALUES (:id, :doc_id, :user_id, :idx, :content, :page, :embedding, :meta)
                    """), {
                        "id": chunk.id,
                        "doc_id": chunk.document_id,
                        "user_id": chunk.user_id,
                        "idx": chunk.chunk_index,
                        "content": chunk.content,
                        "page": chunk.page_number or -1,
                        "embedding": embedding_json,
                        "meta": metadata_json
                    })

                inserted_ids.append(chunk.id)

            conn.commit()

        return inserted_ids

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        user_id: Optional[str] = None,
        document_ids: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[VectorSearchResult]:
        """
        向量相似度检索

        Args:
            query_embedding: 查询向量
            top_k: 返回数量
            user_id: 用户ID过滤
            document_ids: 文档ID列表过滤
            filters: 额外过滤条件 (暂未实现)

        Returns:
            检索结果列表
        """
        if not self._connected:
            self.connect()

        if self._is_postgres and self._pgvector_enabled:
            return self._search_pgvector(query_embedding, top_k, user_id, document_ids)
        else:
            return self._search_brute_force(query_embedding, top_k, user_id, document_ids)

    def _search_pgvector(
        self,
        query_embedding: List[float],
        top_k: int,
        user_id: Optional[str],
        document_ids: Optional[List[str]]
    ) -> List[VectorSearchResult]:
        """使用 pgvector 的原生向量搜索"""
        embedding_str = f"[{','.join(map(str, query_embedding))}]"

        # 构建 WHERE 子句
        where_clauses = []
        params = {"embedding": embedding_str, "top_k": top_k}

        if user_id:
            where_clauses.append("user_id = :user_id")
            params["user_id"] = user_id

        if document_ids:
            placeholders = ", ".join([f":doc_{i}" for i in range(len(document_ids))])
            where_clauses.append(f"document_id IN ({placeholders})")
            for i, doc_id in enumerate(document_ids):
                params[f"doc_{i}"] = doc_id

        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        # 使用余弦距离进行搜索 (1 - cosine_similarity)
        query = f"""
            SELECT
                id,
                document_id,
                user_id,
                chunk_index,
                content,
                page_number,
                metadata,
                1 - (embedding <=> :embedding::vector) AS similarity
            FROM document_embeddings
            {where_sql}
            ORDER BY embedding <=> :embedding::vector
            LIMIT :top_k
        """

        results = []
        with self._engine.connect() as conn:
            rows = conn.execute(text(query), params).fetchall()

            for row in rows:
                metadata = row[6]
                if isinstance(metadata, str):
                    metadata = json.loads(metadata)

                results.append(VectorSearchResult(
                    id=row[0],
                    document_id=row[1],
                    user_id=row[2],
                    chunk_index=row[3],
                    content=row[4],
                    page_number=row[5] if row[5] != -1 else None,
                    score=float(row[7]),  # similarity
                    metadata=metadata or {}
                ))

        return results

    def _search_brute_force(
        self,
        query_embedding: List[float],
        top_k: int,
        user_id: Optional[str],
        document_ids: Optional[List[str]]
    ) -> List[VectorSearchResult]:
        """降级的暴力搜索 (用于 SQLite 测试模式)"""
        # 构建 WHERE 子句
        where_clauses = []
        params = {}

        if user_id:
            where_clauses.append("user_id = :user_id")
            params["user_id"] = user_id

        if document_ids:
            placeholders = ", ".join([f":doc_{i}" for i in range(len(document_ids))])
            where_clauses.append(f"document_id IN ({placeholders})")
            for i, doc_id in enumerate(document_ids):
                params[f"doc_{i}"] = doc_id

        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        query = f"""
            SELECT id, document_id, user_id, chunk_index, content, page_number, embedding, metadata
            FROM document_embeddings
            {where_sql}
        """

        query_vec = np.array(query_embedding)
        query_norm = np.linalg.norm(query_vec)
        if query_norm > 0:
            query_vec = query_vec / query_norm

        candidates = []
        with self._engine.connect() as conn:
            rows = conn.execute(text(query), params).fetchall()

            for row in rows:
                try:
                    embedding = json.loads(row[6]) if isinstance(row[6], str) else row[6]
                    if not embedding:
                        continue

                    doc_vec = np.array(embedding)
                    doc_norm = np.linalg.norm(doc_vec)
                    if doc_norm > 0:
                        doc_vec = doc_vec / doc_norm

                    # 余弦相似度
                    similarity = float(np.dot(query_vec, doc_vec))

                    metadata = json.loads(row[7]) if isinstance(row[7], str) else (row[7] or {})

                    candidates.append(VectorSearchResult(
                        id=row[0],
                        document_id=row[1],
                        user_id=row[2],
                        chunk_index=row[3],
                        content=row[4],
                        page_number=row[5] if row[5] != -1 else None,
                        score=similarity,
                        metadata=metadata
                    ))

                except Exception as e:
                    print(f"处理向量时出错: {e}")
                    continue

        # 按相似度排序并返回 top_k
        candidates.sort(key=lambda x: x.score, reverse=True)
        return candidates[:top_k]

    def delete_by_document(self, document_id: str) -> int:
        """
        删除指定文档的所有分块

        Args:
            document_id: 文档ID

        Returns:
            删除的数量
        """
        if not self._connected:
            self.connect()

        with self._engine.connect() as conn:
            result = conn.execute(text("""
                DELETE FROM document_embeddings WHERE document_id = :doc_id
            """), {"doc_id": document_id})
            conn.commit()
            return result.rowcount

    def delete_by_user(self, user_id: str) -> int:
        """
        删除指定用户的所有分块

        Args:
            user_id: 用户ID

        Returns:
            删除的数量
        """
        if not self._connected:
            self.connect()

        with self._engine.connect() as conn:
            result = conn.execute(text("""
                DELETE FROM document_embeddings WHERE user_id = :user_id
            """), {"user_id": user_id})
            conn.commit()
            return result.rowcount

    def get_collection_stats(self) -> Dict[str, Any]:
        """获取向量表统计信息"""
        if not self._connected:
            self.connect()

        with self._engine.connect() as conn:
            result = conn.execute(text("""
                SELECT COUNT(*) FROM document_embeddings
            """)).fetchone()
            count = result[0] if result else 0

        return {
            "name": "document_embeddings",
            "num_entities": count,
            "dimension": self.dimension,
            "backend": "pgvector" if self._pgvector_enabled else "brute_force",
            "database": "postgresql" if self._is_postgres else "sqlite"
        }


# 便捷函数：根据配置自动选择向量服务
def get_vector_service():
    """
    根据配置自动返回合适的向量服务

    Returns:
        MilvusService 或 PgvectorService 实例
    """
    if settings.VECTOR_STORE_BACKEND == "milvus" and settings.MILVUS_ENABLED:
        from app.services.milvus_service import MilvusService
        return MilvusService()
    else:
        return PgvectorService()
