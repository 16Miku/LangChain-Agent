# ============================================================
# Search API - 检索接口
# ============================================================

from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.security import get_current_user, CurrentUser
from app.config import settings
from app.schemas.search import (
    SearchRequest, SearchResponse, CitationRequest, CitationDetail
)
from app.services.search_service import HybridSearchService
from app.services.bm25_service import BM25Service
from app.services.rerank_service import RerankService
from app.services.citation_service import CitationService

router = APIRouter()

# 全局 Reranker 实例 (避免每次请求都加载模型)
_reranker = None


def get_reranker() -> RerankService:
    """获取或创建 Reranker 实例"""
    global _reranker
    if _reranker is None:
        _reranker = RerankService(model_name=settings.RERANKER_MODEL)
    return _reranker


@router.post("", response_model=SearchResponse)
async def hybrid_search(
    request: SearchRequest,
    http_request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    混合检索

    结合向量相似度检索和 BM25 关键词检索，使用 RRF 算法融合结果。

    Args:
        request: 检索请求
            - query: 查询文本
            - top_k: 返回数量 (默认 10)
            - alpha: 向量权重 (默认 0.5)
            - rerank: 是否重排序 (默认 True)
            - document_ids: 限定文档ID列表
    """
    # 获取服务实例
    milvus_service = http_request.app.state.milvus_service
    embedding_service = http_request.app.state.embedding_service

    # 获取 Reranker (如果启用)
    reranker = None
    if request.rerank and settings.ENABLE_RERANK:
        reranker = get_reranker()

    # 创建 BM25 服务实例 (每次请求新建，从数据库加载索引)
    bm25_service = BM25Service()

    # 转换 document_ids 为字符串列表
    document_ids = None
    if request.document_ids:
        document_ids = [str(doc_id) for doc_id in request.document_ids]

    # 创建混合检索服务
    search_service = HybridSearchService(
        milvus_service=milvus_service,
        embedding_service=embedding_service,
        bm25_service=bm25_service,
        reranker=reranker
    )

    # 执行检索
    try:
        results, search_time_ms = await search_service.search(
            query=request.query,
            top_k=request.top_k,
            alpha=request.alpha,
            user_id=current_user.user_id,
            document_ids=document_ids,
            use_rerank=request.rerank and settings.ENABLE_RERANK,
            db=db
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )

    # 添加引用信息
    enriched_results, citations = CitationService.enrich_search_results(
        results=results,
        query=request.query
    )

    return SearchResponse(
        query=request.query,
        total=len(enriched_results),
        results=enriched_results,
        search_time_ms=search_time_ms,
        citations=citations
    )


@router.post("/vector", response_model=SearchResponse)
async def vector_search(
    request: SearchRequest,
    http_request: Request,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    仅向量检索

    使用向量相似度进行检索，不使用 BM25。
    """
    milvus_service = http_request.app.state.milvus_service
    embedding_service = http_request.app.state.embedding_service

    # 转换 document_ids
    document_ids = None
    if request.document_ids:
        document_ids = [str(doc_id) for doc_id in request.document_ids]

    search_service = HybridSearchService(
        milvus_service=milvus_service,
        embedding_service=embedding_service
    )

    import time
    start_time = time.time()

    results = search_service.vector_only_search(
        query=request.query,
        top_k=request.top_k,
        user_id=current_user.user_id,
        document_ids=document_ids
    )

    search_time_ms = (time.time() - start_time) * 1000

    return SearchResponse(
        query=request.query,
        total=len(results),
        results=results,
        search_time_ms=search_time_ms
    )


@router.post("/bm25", response_model=SearchResponse)
async def bm25_search(
    request: SearchRequest,
    http_request: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    仅 BM25 检索

    使用 BM25 关键词检索，不使用向量。
    """
    # 转换 document_ids
    document_ids = None
    if request.document_ids:
        document_ids = [str(doc_id) for doc_id in request.document_ids]

    # 创建 BM25 服务并加载索引
    bm25_service = BM25Service()
    bm25_service.build_index_from_db(db, current_user.user_id, document_ids)

    import time
    start_time = time.time()

    bm25_results = bm25_service.search(
        query=request.query,
        top_k=request.top_k,
        document_ids=document_ids
    )

    search_time_ms = (time.time() - start_time) * 1000

    # 转换结果
    from app.schemas.search import SearchResult
    results = [
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

    return SearchResponse(
        query=request.query,
        total=len(results),
        results=results,
        search_time_ms=search_time_ms
    )


# ============================================================
# 引用追溯 API
# ============================================================

@router.post("/citations", response_model=List[CitationDetail])
async def get_citations(
    request: CitationRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取引用详情

    根据分块ID列表获取引用详情，包括上下文（前后分块）。

    Args:
        request: 引用追溯请求
            - chunk_ids: 分块ID列表
            - include_context: 是否包含上下文 (默认 True)
            - context_size: 上下文分块数量 (默认 1)
    """
    results = []

    for chunk_id in request.chunk_ids:
        detail = CitationService.get_citation_detail(
            db=db,
            chunk_id=chunk_id,
            include_context=request.include_context,
            context_size=request.context_size
        )
        if detail:
            results.append(detail)

    return results


@router.get("/citations/{chunk_id}", response_model=CitationDetail)
async def get_citation_detail(
    chunk_id: str,
    include_context: bool = True,
    context_size: int = 1,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取单个引用详情

    Args:
        chunk_id: 分块ID
        include_context: 是否包含上下文
        context_size: 上下文分块数量
    """
    detail = CitationService.get_citation_detail(
        db=db,
        chunk_id=chunk_id,
        include_context=include_context,
        context_size=context_size
    )

    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Citation not found: {chunk_id}"
        )

    return detail
