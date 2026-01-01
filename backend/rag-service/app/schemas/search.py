# ============================================================
# Search Schemas
# ============================================================

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID


class SearchRequest(BaseModel):
    """检索请求"""
    query: str = Field(..., min_length=1, description="查询文本")
    top_k: int = Field(default=10, ge=1, le=100, description="返回结果数量")
    alpha: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="向量检索权重 (1-alpha 为 BM25 权重)"
    )
    rerank: bool = Field(default=True, description="是否使用重排序")
    document_ids: Optional[List[UUID]] = Field(
        default=None,
        description="限定在指定文档中检索"
    )
    filters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="额外过滤条件"
    )


class Citation(BaseModel):
    """引用来源"""
    chunk_id: str
    document_id: str
    document_name: str
    page_number: Optional[int] = None
    content: str
    score: float
    metadata: Optional[Dict[str, Any]] = None


class SearchResult(BaseModel):
    """单条检索结果"""
    chunk_id: str
    document_id: str
    document_name: str
    content: str
    page_number: Optional[int] = None
    score: float
    vector_score: Optional[float] = None
    bm25_score: Optional[float] = None
    rerank_score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class SearchResponse(BaseModel):
    """检索响应"""
    query: str
    total: int
    results: List[SearchResult]
    search_time_ms: float


class HybridSearchDebug(BaseModel):
    """混合检索调试信息"""
    vector_results_count: int
    bm25_results_count: int
    fused_results_count: int
    reranked: bool
