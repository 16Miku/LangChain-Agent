# ============================================================
# Milvus Service - 向量数据库服务
# ============================================================

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import uuid

from pymilvus import (
    connections,
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType,
    utility
)

from app.config import settings


@dataclass
class ChunkData:
    """分块数据"""
    id: str
    document_id: str
    user_id: str
    chunk_index: int
    content: str
    page_number: Optional[int]
    embedding: List[float]
    metadata: Dict[str, Any]


@dataclass
class VectorSearchResult:
    """向量检索结果"""
    id: str
    document_id: str
    user_id: str
    chunk_index: int
    content: str
    page_number: Optional[int]
    score: float
    metadata: Dict[str, Any]


class MilvusService:
    """Milvus 向量数据库服务"""

    def __init__(self):
        """初始化 Milvus 连接"""
        self.host = settings.MILVUS_HOST
        self.port = settings.MILVUS_PORT
        self.collection_name = settings.MILVUS_COLLECTION
        self.dimension = settings.EMBEDDING_DIMENSION
        self._collection: Optional[Collection] = None
        self._connected = False

    def connect(self) -> bool:
        """连接到 Milvus"""
        try:
            connections.connect(
                alias="default",
                host=self.host,
                port=self.port
            )
            self._connected = True
            print(f"Connected to Milvus at {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Failed to connect to Milvus: {e}")
            self._connected = False
            return False

    def is_connected(self) -> bool:
        """检查是否已连接"""
        if not self._connected:
            return False
        try:
            # 尝试执行简单操作验证连接
            utility.list_collections()
            return True
        except Exception:
            self._connected = False
            return False

    def ensure_collection(self) -> Collection:
        """确保 Collection 存在，如果不存在则创建"""
        if not self._connected:
            self.connect()

        if utility.has_collection(self.collection_name):
            self._collection = Collection(self.collection_name)
            self._collection.load()
            print(f"Loaded existing collection: {self.collection_name}")
        else:
            self._collection = self._create_collection()
            print(f"Created new collection: {self.collection_name}")

        return self._collection

    def _create_collection(self) -> Collection:
        """
        创建 Milvus Collection

        Schema:
        - id: 主键 (VARCHAR)
        - document_id: 文档ID (VARCHAR)
        - user_id: 用户ID (VARCHAR)
        - chunk_index: 分块索引 (INT64)
        - content: 文本内容 (VARCHAR)
        - page_number: 页码 (INT64)
        - embedding: 向量 (FLOAT_VECTOR)
        - metadata: 元数据 (JSON)
        """
        fields = [
            FieldSchema(
                name="id",
                dtype=DataType.VARCHAR,
                is_primary=True,
                max_length=36
            ),
            FieldSchema(
                name="document_id",
                dtype=DataType.VARCHAR,
                max_length=36
            ),
            FieldSchema(
                name="user_id",
                dtype=DataType.VARCHAR,
                max_length=36
            ),
            FieldSchema(
                name="chunk_index",
                dtype=DataType.INT64
            ),
            FieldSchema(
                name="content",
                dtype=DataType.VARCHAR,
                max_length=65535
            ),
            FieldSchema(
                name="page_number",
                dtype=DataType.INT64
            ),
            FieldSchema(
                name="embedding",
                dtype=DataType.FLOAT_VECTOR,
                dim=self.dimension
            ),
            FieldSchema(
                name="metadata",
                dtype=DataType.JSON
            )
        ]

        schema = CollectionSchema(
            fields=fields,
            description="Document chunks for RAG retrieval"
        )

        collection = Collection(
            name=self.collection_name,
            schema=schema
        )

        # 创建索引
        index_params = {
            "metric_type": "IP",  # Inner Product (cosine similarity with normalized vectors)
            "index_type": "IVF_FLAT",
            "params": {"nlist": 1024}
        }
        collection.create_index(
            field_name="embedding",
            index_params=index_params
        )

        # 加载到内存
        collection.load()

        return collection

    def insert(self, chunks: List[ChunkData]) -> List[str]:
        """
        批量插入分块数据

        Args:
            chunks: 分块数据列表

        Returns:
            插入的 ID 列表
        """
        if not self._collection:
            self.ensure_collection()

        data = [
            [chunk.id for chunk in chunks],
            [chunk.document_id for chunk in chunks],
            [chunk.user_id for chunk in chunks],
            [chunk.chunk_index for chunk in chunks],
            [chunk.content for chunk in chunks],
            [chunk.page_number or -1 for chunk in chunks],
            [chunk.embedding for chunk in chunks],
            [chunk.metadata for chunk in chunks]
        ]

        self._collection.insert(data)
        self._collection.flush()

        return [chunk.id for chunk in chunks]

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
            filters: 额外过滤条件

        Returns:
            检索结果列表
        """
        if not self._collection:
            self.ensure_collection()

        # 构建过滤表达式
        expr_parts = []
        if user_id:
            expr_parts.append(f'user_id == "{user_id}"')
        if document_ids:
            doc_ids_str = '", "'.join(document_ids)
            expr_parts.append(f'document_id in ["{doc_ids_str}"]')

        expr = " and ".join(expr_parts) if expr_parts else None

        # 搜索参数
        search_params = {
            "metric_type": "IP",
            "params": {"nprobe": 10}
        }

        results = self._collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            expr=expr,
            output_fields=["document_id", "user_id", "chunk_index", "content", "page_number", "metadata"]
        )

        # 转换结果
        search_results = []
        for hits in results:
            for hit in hits:
                search_results.append(VectorSearchResult(
                    id=hit.id,
                    document_id=hit.entity.get("document_id"),
                    user_id=hit.entity.get("user_id"),
                    chunk_index=hit.entity.get("chunk_index"),
                    content=hit.entity.get("content"),
                    page_number=hit.entity.get("page_number") if hit.entity.get("page_number") != -1 else None,
                    score=hit.score,
                    metadata=hit.entity.get("metadata", {})
                ))

        return search_results

    def delete_by_document(self, document_id: str) -> int:
        """
        删除指定文档的所有分块

        Args:
            document_id: 文档ID

        Returns:
            删除的数量
        """
        if not self._collection:
            self.ensure_collection()

        expr = f'document_id == "{document_id}"'
        result = self._collection.delete(expr)
        self._collection.flush()

        return result.delete_count if hasattr(result, 'delete_count') else 0

    def delete_by_user(self, user_id: str) -> int:
        """
        删除指定用户的所有分块

        Args:
            user_id: 用户ID

        Returns:
            删除的数量
        """
        if not self._collection:
            self.ensure_collection()

        expr = f'user_id == "{user_id}"'
        result = self._collection.delete(expr)
        self._collection.flush()

        return result.delete_count if hasattr(result, 'delete_count') else 0

    def get_collection_stats(self) -> Dict[str, Any]:
        """获取 Collection 统计信息"""
        if not self._collection:
            self.ensure_collection()

        return {
            "name": self.collection_name,
            "num_entities": self._collection.num_entities,
            "dimension": self.dimension
        }
