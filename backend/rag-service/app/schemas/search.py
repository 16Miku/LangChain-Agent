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
    """引用来源 - 用于引用追溯"""
    chunk_id: str = Field(..., description="分块ID")
    document_id: str = Field(..., description="文档ID")
    document_name: str = Field(..., description="文档名称")
    page_number: Optional[int] = Field(None, description="页码")
    section: Optional[str] = Field(None, description="章节标题")
    content: str = Field(..., description="引用的内容")
    content_preview: Optional[str] = Field(None, description="内容预览 (前100字)")
    score: float = Field(..., description="相关性分数")
    highlight_ranges: Optional[List[Dict[str, int]]] = Field(
        None,
        description="高亮位置 [{start: int, end: int}]"
    )
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")


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
    # 引用追溯相关
    citation: Optional[Citation] = Field(None, description="引用信息")


class SearchResponse(BaseModel):
    """检索响应"""
    query: str
    total: int
    results: List[SearchResult]
    search_time_ms: float
    # 引用追溯汇总
    citations: Optional[List[Citation]] = Field(None, description="所有引用来源汇总")


class HybridSearchDebug(BaseModel):
    """混合检索调试信息"""
    vector_results_count: int
    bm25_results_count: int
    fused_results_count: int
    reranked: bool


class CitationRequest(BaseModel):
    """引用追溯请求"""
    chunk_ids: List[str] = Field(..., description="分块ID列表")
    include_context: bool = Field(
        default=True,
        description="是否包含上下文 (前后分块)"
    )
    context_size: int = Field(
        default=1,
        ge=0,
        le=3,
        description="上下文分块数量"
    )


class CitationDetail(BaseModel):
    """引用详情"""
    chunk_id: str
    document_id: str
    document_name: str
    page_number: Optional[int] = None
    chunk_index: int
    content: str
    # 上下文
    prev_chunks: Optional[List[str]] = Field(None, description="前面的分块内容")
    next_chunks: Optional[List[str]] = Field(None, description="后面的分块内容")
    # 文档信息
    total_chunks: int = Field(..., description="文档总分块数")
    metadata: Optional[Dict[str, Any]] = None
