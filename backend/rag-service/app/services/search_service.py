# ============================================================
# Hybrid Search Service - 混合检索服务
# 结合向量检索和 BM25 关键词检索
# 支持查询改写优化
# ============================================================

from typing import List, Dict, Any, Optional, TYPE_CHECKING, Union
from dataclasses import dataclass
import time

from sqlalchemy.orm import Session

from app.config import settings
from app.services.milvus_service import VectorSearchResult
from app.services.bm25_service import BM25Service, BM25Result
from app.services.embedding_service import EmbeddingService
from app.services.query_rewriter import QueryRewriterService, get_query_rewriter
from app.schemas.search import SearchResult

if TYPE_CHECKING:
    from app.services.rerank_service import RerankService
    from app.services.milvus_service import MilvusService
    from app.services.pgvector_service import PgvectorService


@dataclass
class FusedResult:
    """融合后的结果"""
    chunk_id: str
    document_id: str
    content: str
    page_number: Optional[int]
    fused_score: float
    vector_score: Optional[float]
    bm25_score: Optional[float]
    rerank_score: Optional[float] = None  # 重排序分数
    metadata: Dict[str, Any] = None


class HybridSearchService:
    """
    混合检索服务

    支持:
    - 向量相似度检索 (Milvus 或 pgvector)
    - BM25 关键词检索
    - RRF (Reciprocal Rank Fusion) 融合
    - Reranker 重排序 (可选)
    """

    def __init__(
        self,
        milvus_service,  # MilvusService 或 PgvectorService
        embedding_service: EmbeddingService,
        bm25_service: Optional[BM25Service] = None,
        reranker=None
    ):
        """
        初始化混合检索服务

        Args:
            milvus_service: 向量检索服务 (MilvusService 或 PgvectorService)
            embedding_service: 嵌入服务
            bm25_service: BM25 检索服务 (可选)
            reranker: 重排序模型 (可选)
        """
        self.milvus = milvus_service
        self.embedding = embedding_service
        self.bm25 = bm25_service
        self.reranker = reranker

    def rrf_fusion(
        self,
        vector_results: List[VectorSearchResult],
        bm25_results: List[BM25Result],
        alpha: float = 0.5,
        k: int = 60
    ) -> List[FusedResult]:
        """
        Reciprocal Rank Fusion (RRF) 融合算法

        公式: RRF(d) = sum(1 / (k + r_i)) for each ranking r_i

        Args:
            vector_results: 向量检索结果
            bm25_results: BM25 检索结果
            alpha: 向量检索权重 (1-alpha 为 BM25 权重)
            k: RRF 常数 (默认 60)

        Returns:
            融合后的结果列表
        """
        scores: Dict[str, Dict[str, Any]] = {}

        # 处理向量检索结果
        for rank, result in enumerate(vector_results):
            chunk_id = result.id
            rrf_score = alpha / (k + rank + 1)

            if chunk_id not in scores:
                scores[chunk_id] = {
                    "document_id": result.document_id,
                    "content": result.content,
                    "page_number": result.page_number,
                    "metadata": result.metadata,
                    "fused_score": 0,
                    "vector_score": result.score,
                    "bm25_score": None
                }

            scores[chunk_id]["fused_score"] += rrf_score

        # 处理 BM25 结果
        for rank, result in enumerate(bm25_results):
            chunk_id = result.chunk_id
            rrf_score = (1 - alpha) / (k + rank + 1)

            if chunk_id not in scores:
                scores[chunk_id] = {
                    "document_id": result.document_id,
                    "content": result.content,
                    "page_number": result.page_number,
                    "metadata": result.metadata,
                    "fused_score": 0,
                    "vector_score": None,
                    "bm25_score": result.score
                }
            else:
                scores[chunk_id]["bm25_score"] = result.score

            scores[chunk_id]["fused_score"] += rrf_score

        # 按融合分数排序
        sorted_results = sorted(
            scores.items(),
            key=lambda x: x[1]["fused_score"],
            reverse=True
        )

        # 构建结果
        fused_results = []
        for chunk_id, data in sorted_results:
            fused_results.append(FusedResult(
                chunk_id=chunk_id,
                document_id=data["document_id"],
                content=data["content"],
                page_number=data["page_number"],
                fused_score=data["fused_score"],
                vector_score=data["vector_score"],
                bm25_score=data["bm25_score"],
                metadata=data["metadata"]
            ))

        return fused_results

    async def search(
        self,
        query: str,
        top_k: int = 10,
        alpha: float = 0.5,
        user_id: Optional[str] = None,
        document_ids: Optional[List[str]] = None,
        use_rerank: bool = True,
        db: Optional[Session] = None
    ) -> tuple[List[SearchResult], float]:
        """
        执行混合检索

        Args:
            query: 查询文本
            top_k: 返回数量
            alpha: 向量权重 (0-1)
            user_id: 用户ID
            document_ids: 限定文档ID列表
            use_rerank: 是否使用重排序
            db: 数据库会话 (用于 BM25)

        Returns:
            (检索结果列表, 检索耗时ms)
        """
        start_time = time.time()

        # 1. 向量检索 (如果 Milvus 可用)
        vector_results: List[VectorSearchResult] = []
        if self.milvus is not None:
            query_embedding = self.embedding.embed_query(query)
            vector_results = self.milvus.search(
                query_embedding=query_embedding,
                top_k=top_k * 2,  # 检索更多用于融合
                user_id=user_id,
                document_ids=document_ids
            )

        # 2. BM25 检索 (如果可用)
        bm25_results: List[BM25Result] = []
        if self.bm25 and alpha < 1.0:
            # 如果 BM25 索引为空且有数据库会话，重建索引
            if self.bm25.doc_count == 0 and db:
                self.bm25.build_index_from_db(db, user_id, document_ids)

            bm25_results = self.bm25.search(
                query=query,
                top_k=top_k * 2,
                document_ids=document_ids
            )

        # 3. 融合结果
        if bm25_results and vector_results:
            fused_results = self.rrf_fusion(
                vector_results,
                bm25_results,
                alpha=alpha
            )
        elif vector_results:
            # 只有向量结果
            fused_results = [
                FusedResult(
                    chunk_id=r.id,
                    document_id=r.document_id,
                    content=r.content,
                    page_number=r.page_number,
                    fused_score=r.score,
                    vector_score=r.score,
                    bm25_score=None,
                    metadata=r.metadata
                )
                for r in vector_results
            ]
        elif bm25_results:
            # 只有 BM25 结果
            fused_results = [
                FusedResult(
                    chunk_id=r.chunk_id,
                    document_id=r.document_id,
                    content=r.content,
                    page_number=r.page_number,
                    fused_score=r.score,
                    vector_score=None,
                    bm25_score=r.score,
                    metadata=r.metadata
                )
                for r in bm25_results
            ]
        else:
            fused_results = []

        # 4. 重排序 (如果可用)
        if use_rerank and self.reranker and fused_results:
            fused_results = await self._rerank(query, fused_results, top_k)
        else:
            fused_results = fused_results[:top_k]

        # 5. 转换为 SearchResult
        search_results = []
        for result in fused_results:
            search_results.append(SearchResult(
                chunk_id=result.chunk_id,
                document_id=result.document_id,
                document_name=result.metadata.get("filename", "Unknown") if result.metadata else "Unknown",
                content=result.content,
                page_number=result.page_number,
                score=result.fused_score,
                vector_score=result.vector_score,
                bm25_score=result.bm25_score,
                rerank_score=result.rerank_score,
                metadata=result.metadata
            ))

        elapsed_time = (time.time() - start_time) * 1000
        return search_results, elapsed_time

    async def _rerank(
        self,
        query: str,
        results: List[FusedResult],
        top_k: int
    ) -> List[FusedResult]:
        """
        使用 Reranker 重排序

        Args:
            query: 查询文本
            results: 融合后的结果
            top_k: 返回数量

        Returns:
            重排序后的结果
        """
        if not self.reranker:
            return results[:top_k]

        try:
            # 准备数据格式
            rerank_input = [
                {
                    "chunk_id": r.chunk_id,
                    "document_id": r.document_id,
                    "content": r.content,
                    "score": r.fused_score,
                    "metadata": r.metadata
                }
                for r in results
            ]

            # 调用 RerankService
            reranked = self.reranker.rerank(query, rerank_input, top_k)

            # 转换回 FusedResult
            reranked_results = []
            for rr in reranked:
                # 找到原始结果
                original = next(
                    (r for r in results if r.chunk_id == rr.chunk_id),
                    None
                )
                if original:
                    reranked_results.append(FusedResult(
                        chunk_id=rr.chunk_id,
                        document_id=rr.document_id,
                        content=rr.content,
                        page_number=original.page_number,
                        fused_score=rr.rerank_score,  # 使用重排序分数
                        vector_score=original.vector_score,
                        bm25_score=original.bm25_score,
                        rerank_score=rr.rerank_score,  # 记录重排序分数
                        metadata=rr.metadata
                    ))

            return reranked_results

        except Exception as e:
            print(f"Reranking failed: {e}")
            return results[:top_k]

    def vector_only_search(
        self,
        query: str,
        top_k: int = 10,
        user_id: Optional[str] = None,
        document_ids: Optional[List[str]] = None
    ) -> List[SearchResult]:
        """
        仅向量检索

        Args:
            query: 查询文本
            top_k: 返回数量
            user_id: 用户ID
            document_ids: 限定文档ID列表

        Returns:
            检索结果列表
        """
        if self.milvus is None:
            return []

        query_embedding = self.embedding.embed_query(query)
        vector_results = self.milvus.search(
            query_embedding=query_embedding,
            top_k=top_k,
            user_id=user_id,
            document_ids=document_ids
        )

        return [
            SearchResult(
                chunk_id=r.id,
                document_id=r.document_id,
                document_name=r.metadata.get("filename", "Unknown"),
                content=r.content,
                page_number=r.page_number,
                score=r.score,
                vector_score=r.score,
                bm25_score=None,
                rerank_score=None,
                metadata=r.metadata
            )
            for r in vector_results
        ]

    def bm25_only_search(
        self,
        query: str,
        top_k: int = 10,
        document_ids: Optional[List[str]] = None
    ) -> List[SearchResult]:
        """
        仅 BM25 检索

        Args:
            query: 查询文本
            top_k: 返回数量
            document_ids: 限定文档ID列表

        Returns:
            检索结果列表
        """
        if not self.bm25:
            return []

        bm25_results = self.bm25.search(
            query=query,
            top_k=top_k,
            document_ids=document_ids
        )

        return [
            SearchResult(
                chunk_id=r.chunk_id,
                document_id=r.document_id,
                document_name=r.metadata.get("filename", "Unknown"),
                content=r.content,
                page_number=r.page_number,
                score=r.score,
                vector_score=None,
                bm25_score=r.score,
                rerank_score=None,
                metadata=r.metadata
            )
            for r in bm25_results
        ]

    async def search_with_rewrite(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        top_k: int = 10,
        alpha: float = 0.5,
        user_id: Optional[str] = None,
        document_ids: Optional[List[str]] = None,
        use_rerank: bool = True,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        带查询改写的混合检索

        基于对话历史自动改写查询，解析指代词，补充上下文信息

        Args:
            query: 用户原始查询
            conversation_history: 对话历史，格式为 [{"role": "user/assistant", "content": "..."}]
            top_k: 返回数量
            alpha: 向量权重 (0-1)
            user_id: 用户ID
            document_ids: 限定文档ID列表
            use_rerank: 是否使用重排序
            db: 数据库会话

        Returns:
            {
                "results": List[SearchResult],  # 检索结果
                "search_time_ms": float,        # 检索耗时
                "rewrite_info": {               # 查询改写信息
                    "main_query": str,          # 改写后的主查询
                    "variants": List[str],      # 查询变体
                    "reasoning": str,           # 改写理由
                    "entities": List[str],      # 识别的实体
                    "original_query": str,      # 原始查询
                    "was_rewritten": bool       # 是否进行了改写
                } | None
            }
        """
        rewrite_info = None
        search_query = query

        # 如果有对话历史，尝试改写查询
        if conversation_history:
            try:
                rewriter = get_query_rewriter()
                rewrite_info = await rewriter.rewrite(query, conversation_history)
                search_query = rewrite_info.get("main_query", query)
            except Exception as e:
                print(f"[HybridSearch] 查询改写失败，使用原始查询: {e}")
                rewrite_info = None

        # 执行检索
        results, search_time_ms = await self.search(
            query=search_query,
            top_k=top_k,
            alpha=alpha,
            user_id=user_id,
            document_ids=document_ids,
            use_rerank=use_rerank,
            db=db
        )

        return {
            "results": results,
            "search_time_ms": search_time_ms,
            "rewrite_info": rewrite_info
        }

    async def search_with_multi_turn_rewrite(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        previous_results: Optional[List[Dict[str, Any]]] = None,
        top_k: int = 10,
        alpha: float = 0.5,
        user_id: Optional[str] = None,
        document_ids: Optional[List[str]] = None,
        use_rerank: bool = True,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        多轮对话检索优化

        考虑之前的检索结果，避免重复检索，生成能够补充新信息的查询

        Args:
            query: 用户原始查询
            conversation_history: 对话历史
            previous_results: 之前的检索结果，用于避免重复
            top_k: 返回数量
            alpha: 向量权重
            user_id: 用户ID
            document_ids: 限定文档ID列表
            use_rerank: 是否使用重排序
            db: 数据库会话

        Returns:
            {
                "results": List[SearchResult],
                "search_time_ms": float,
                "rewrite_info": Dict | None
            }
        """
        rewrite_info = None
        search_query = query

        # 多轮对话查询优化
        if conversation_history or previous_results:
            try:
                rewriter = get_query_rewriter()
                rewrite_info = await rewriter.rewrite_for_multi_turn(
                    query=query,
                    conversation_history=conversation_history or [],
                    previous_results=previous_results
                )
                search_query = rewrite_info.get("main_query", query)
            except Exception as e:
                print(f"[HybridSearch] 多轮查询优化失败，使用原始查询: {e}")
                rewrite_info = None

        # 执行检索
        results, search_time_ms = await self.search(
            query=search_query,
            top_k=top_k,
            alpha=alpha,
            user_id=user_id,
            document_ids=document_ids,
            use_rerank=use_rerank,
            db=db
        )

        return {
            "results": results,
            "search_time_ms": search_time_ms,
            "rewrite_info": rewrite_info
        }
