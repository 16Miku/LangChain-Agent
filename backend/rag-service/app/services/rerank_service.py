# ============================================================
# Rerank Service - 重排序服务
# ============================================================
# 使用 BGE-Reranker 或 sentence-transformers 交叉编码器
# 对检索结果进行二次排序，提升相关性准确度

from typing import List, Optional, Tuple
from dataclasses import dataclass

from app.config import settings


@dataclass
class RerankResult:
    """重排序结果"""
    chunk_id: str
    document_id: str
    content: str
    original_score: float
    rerank_score: float
    metadata: dict


class RerankService:
    """
    重排序服务

    支持两种模式:
    1. CrossEncoder 模式 (sentence-transformers)
    2. 简化模式 (基于关键词匹配的轻量级重排序)
    """

    def __init__(self, model_name: str = "BAAI/bge-reranker-base"):
        """
        初始化重排序服务

        Args:
            model_name: 重排序模型名称
                - "BAAI/bge-reranker-base": BGE 重排序模型 (推荐)
                - "cross-encoder/ms-marco-MiniLM-L-6-v2": 轻量级英文模型
        """
        self.model_name = model_name
        self.model = None
        self.use_cross_encoder = settings.RERANKER_ENABLED

        if self.use_cross_encoder:
            self._load_model()

    def _load_model(self):
        """加载重排序模型"""
        try:
            from sentence_transformers import CrossEncoder

            print(f"Loading reranker model: {self.model_name}")
            self.model = CrossEncoder(self.model_name, max_length=512)
            print("Reranker model loaded successfully")

        except ImportError:
            print("sentence-transformers not installed, using simple reranker")
            self.use_cross_encoder = False
        except Exception as e:
            print(f"Failed to load reranker model: {e}, using simple reranker")
            self.use_cross_encoder = False

    def rerank(
        self,
        query: str,
        results: List[dict],
        top_k: int = 10
    ) -> List[RerankResult]:
        """
        对检索结果进行重排序

        Args:
            query: 查询文本
            results: 原始检索结果列表，每个结果包含:
                - chunk_id: 分块ID
                - document_id: 文档ID
                - content: 文本内容
                - score: 原始分数
                - metadata: 元数据
            top_k: 返回的最大结果数

        Returns:
            重排序后的结果列表
        """
        if not results:
            return []

        if self.use_cross_encoder and self.model is not None:
            return self._rerank_with_cross_encoder(query, results, top_k)
        else:
            return self._simple_rerank(query, results, top_k)

    def _rerank_with_cross_encoder(
        self,
        query: str,
        results: List[dict],
        top_k: int
    ) -> List[RerankResult]:
        """
        使用 CrossEncoder 进行重排序
        """
        # 构建查询-文档对
        pairs = [(query, r.get("content", "")) for r in results]

        # 计算重排序分数
        scores = self.model.predict(pairs)

        # 组合结果
        reranked = []
        for i, (result, score) in enumerate(zip(results, scores)):
            reranked.append(RerankResult(
                chunk_id=result.get("chunk_id", ""),
                document_id=result.get("document_id", ""),
                content=result.get("content", ""),
                original_score=result.get("score", 0.0),
                rerank_score=float(score),
                metadata=result.get("metadata", {})
            ))

        # 按重排序分数排序
        reranked.sort(key=lambda x: x.rerank_score, reverse=True)

        return reranked[:top_k]

    def _simple_rerank(
        self,
        query: str,
        results: List[dict],
        top_k: int
    ) -> List[RerankResult]:
        """
        简化的重排序 (基于关键词匹配)

        计算方法:
        1. 查询词在文档中的出现次数
        2. 查询词的位置权重 (越靠前权重越高)
        3. 与原始分数加权融合
        """
        import jieba

        # 分词
        query_terms = set(jieba.cut(query))
        query_terms = {t for t in query_terms if len(t) > 1}  # 过滤单字

        reranked = []
        for result in results:
            content = result.get("content", "")
            content_lower = content.lower()

            # 计算关键词匹配分数
            match_score = 0.0
            position_score = 0.0

            for term in query_terms:
                # 出现次数
                count = content_lower.count(term.lower())
                match_score += count

                # 位置分数 (越靠前越高)
                pos = content_lower.find(term.lower())
                if pos >= 0:
                    position_score += 1.0 / (1 + pos / 100)

            # 归一化
            if query_terms:
                match_score = match_score / len(query_terms)
                position_score = position_score / len(query_terms)

            # 融合分数: 原始分数 + 匹配分数 + 位置分数
            original_score = result.get("score", 0.0)
            rerank_score = (
                0.5 * original_score +
                0.3 * match_score +
                0.2 * position_score
            )

            reranked.append(RerankResult(
                chunk_id=result.get("chunk_id", ""),
                document_id=result.get("document_id", ""),
                content=content,
                original_score=original_score,
                rerank_score=rerank_score,
                metadata=result.get("metadata", {})
            ))

        # 按重排序分数排序
        reranked.sort(key=lambda x: x.rerank_score, reverse=True)

        return reranked[:top_k]

    async def rerank_async(
        self,
        query: str,
        results: List[dict],
        top_k: int = 10
    ) -> List[RerankResult]:
        """
        异步重排序 (包装同步方法)
        """
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.rerank,
            query,
            results,
            top_k
        )
