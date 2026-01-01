# ============================================================
# Search API - 检索接口
# ============================================================

from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.security import get_current_user, CurrentUser
from app.config import settings
from app.schemas.search import SearchRequest, SearchResponse
from app.services.search_service import HybridSearchService
from app.services.bm25_service import BM25Service

router = APIRouter()


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
        reranker=None  # TODO: 集成 reranker
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

    return SearchResponse(
        query=request.query,
        total=len(results),
        results=results,
        search_time_ms=search_time_ms
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
