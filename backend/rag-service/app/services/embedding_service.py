# ============================================================
# Embedding Service - 文本向量化服务
# ============================================================

from typing import List, Union
from sentence_transformers import SentenceTransformer
import numpy as np

from app.config import settings


class EmbeddingService:
    """文本向量化服务"""

    def __init__(self, model_name: str = None):
        """初始化 Embedding 模型"""
        model_name = model_name or settings.EMBEDDING_MODEL
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.dimension = settings.EMBEDDING_DIMENSION
        print(f"Embedding model loaded, dimension: {self.dimension}")

    def embed(self, text: Union[str, List[str]]) -> np.ndarray:
        """
        将文本转换为向量

        Args:
            text: 单个文本或文本列表

        Returns:
            向量数组 (n, dim) 或 (dim,)
        """
        if isinstance(text, str):
            return self.model.encode(text, normalize_embeddings=True)
        return self.model.encode(text, normalize_embeddings=True)

    def embed_query(self, query: str) -> List[float]:
        """
        嵌入查询文本

        Args:
            query: 查询文本

        Returns:
            向量列表
        """
        embedding = self.embed(query)
        return embedding.tolist()

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """
        批量嵌入文档

        Args:
            documents: 文档列表

        Returns:
            向量列表的列表
        """
        embeddings = self.embed(documents)
        return embeddings.tolist()

    def get_dimension(self) -> int:
        """获取向量维度"""
        return self.dimension
