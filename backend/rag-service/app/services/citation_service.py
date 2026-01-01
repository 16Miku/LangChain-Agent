# ============================================================
# Citation Service - 引用追溯服务
# ============================================================
# 提供引用来源追溯、上下文获取、高亮等功能

from typing import List, Optional, Dict, Any, Tuple
import re

from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.chunk import Chunk
from app.models.document import Document
from app.schemas.search import Citation, CitationDetail, SearchResult


class CitationService:
    """
    引用追溯服务

    功能:
    1. 生成引用信息 (Citation)
    2. 获取引用上下文 (前后分块)
    3. 计算高亮位置
    4. 生成引用预览
    """

    @staticmethod
    def create_citation(
        chunk_id: str,
        document_id: str,
        document_name: str,
        content: str,
        score: float,
        page_number: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        query: Optional[str] = None
    ) -> Citation:
        """
        创建引用对象

        Args:
            chunk_id: 分块ID
            document_id: 文档ID
            document_name: 文档名称
            content: 分块内容
            score: 相关性分数
            page_number: 页码
            metadata: 元数据
            query: 查询文本 (用于高亮)

        Returns:
            Citation 对象
        """
        # 生成内容预览 (前100字)
        content_preview = content[:100] + "..." if len(content) > 100 else content

        # 提取章节标题 (如果有)
        section = CitationService._extract_section(content, metadata)

        # 计算高亮位置 (如果有查询)
        highlight_ranges = None
        if query:
            highlight_ranges = CitationService._find_highlight_ranges(content, query)

        return Citation(
            chunk_id=chunk_id,
            document_id=document_id,
            document_name=document_name,
            page_number=page_number,
            section=section,
            content=content,
            content_preview=content_preview,
            score=score,
            highlight_ranges=highlight_ranges,
            metadata=metadata
        )

    @staticmethod
    def _extract_section(content: str, metadata: Optional[Dict[str, Any]]) -> Optional[str]:
        """
        提取章节标题

        Args:
            content: 内容
            metadata: 元数据

        Returns:
            章节标题或 None
        """
        # 优先从 metadata 获取
        if metadata and "section" in metadata:
            return metadata["section"]

        # 尝试从内容中提取标题 (如 [Page X] 后的第一行)
        lines = content.strip().split("\n")
        for line in lines[:3]:  # 只看前3行
            line = line.strip()
            # 跳过 [Page X] 标记
            if line.startswith("[Page"):
                continue
            # 如果是短行且不以标点结尾，可能是标题
            if line and len(line) < 50 and not line.endswith(("。", ".", "，", ",", "；", ";")):
                return line

        return None

    @staticmethod
    def _find_highlight_ranges(
        content: str,
        query: str
    ) -> List[Dict[str, int]]:
        """
        查找需要高亮的文本位置

        Args:
            content: 内容
            query: 查询文本

        Returns:
            高亮位置列表 [{start, end}]
        """
        import jieba

        # 分词
        query_terms = set(jieba.cut(query))
        query_terms = {t.lower() for t in query_terms if len(t) > 1}

        ranges = []
        content_lower = content.lower()

        for term in query_terms:
            # 查找所有出现位置
            start = 0
            while True:
                pos = content_lower.find(term, start)
                if pos == -1:
                    break
                ranges.append({
                    "start": pos,
                    "end": pos + len(term)
                })
                start = pos + 1

        # 按位置排序并合并重叠区间
        ranges.sort(key=lambda x: x["start"])
        merged = []
        for r in ranges:
            if merged and r["start"] <= merged[-1]["end"]:
                merged[-1]["end"] = max(merged[-1]["end"], r["end"])
            else:
                merged.append(r)

        return merged

    @staticmethod
    def get_citation_detail(
        db: Session,
        chunk_id: str,
        include_context: bool = True,
        context_size: int = 1
    ) -> Optional[CitationDetail]:
        """
        获取引用详情 (包含上下文)

        Args:
            db: 数据库会话
            chunk_id: 分块ID
            include_context: 是否包含上下文
            context_size: 上下文分块数量

        Returns:
            CitationDetail 或 None
        """
        # 获取目标分块
        chunk = db.query(Chunk).filter(Chunk.id == chunk_id).first()
        if not chunk:
            return None

        # 获取文档信息
        document = db.query(Document).filter(Document.id == chunk.document_id).first()
        if not document:
            return None

        # 获取同文档的所有分块数量
        total_chunks = db.query(Chunk).filter(
            Chunk.document_id == chunk.document_id
        ).count()

        # 获取上下文分块
        prev_chunks = []
        next_chunks = []

        if include_context and context_size > 0:
            # 获取前面的分块
            prev_results = db.query(Chunk).filter(
                and_(
                    Chunk.document_id == chunk.document_id,
                    Chunk.chunk_index < chunk.chunk_index,
                    Chunk.chunk_index >= chunk.chunk_index - context_size
                )
            ).order_by(Chunk.chunk_index.asc()).all()

            prev_chunks = [c.content for c in prev_results]

            # 获取后面的分块
            next_results = db.query(Chunk).filter(
                and_(
                    Chunk.document_id == chunk.document_id,
                    Chunk.chunk_index > chunk.chunk_index,
                    Chunk.chunk_index <= chunk.chunk_index + context_size
                )
            ).order_by(Chunk.chunk_index.asc()).all()

            next_chunks = [c.content for c in next_results]

        return CitationDetail(
            chunk_id=str(chunk.id),
            document_id=str(chunk.document_id),
            document_name=document.filename,
            page_number=chunk.page_number,
            chunk_index=chunk.chunk_index,
            content=chunk.content,
            prev_chunks=prev_chunks if prev_chunks else None,
            next_chunks=next_chunks if next_chunks else None,
            total_chunks=total_chunks,
            metadata=chunk.extra_data
        )

    @staticmethod
    def batch_get_citations(
        db: Session,
        chunk_ids: List[str]
    ) -> List[CitationDetail]:
        """
        批量获取引用详情

        Args:
            db: 数据库会话
            chunk_ids: 分块ID列表

        Returns:
            CitationDetail 列表
        """
        results = []
        for chunk_id in chunk_ids:
            detail = CitationService.get_citation_detail(
                db, chunk_id, include_context=False
            )
            if detail:
                results.append(detail)
        return results

    @staticmethod
    def enrich_search_results(
        results: List[SearchResult],
        query: str
    ) -> Tuple[List[SearchResult], List[Citation]]:
        """
        为检索结果添加引用信息

        Args:
            results: 检索结果列表
            query: 查询文本

        Returns:
            (增强后的结果列表, 引用列表)
        """
        citations = []
        enriched_results = []

        for result in results:
            # 创建引用
            citation = CitationService.create_citation(
                chunk_id=result.chunk_id,
                document_id=result.document_id,
                document_name=result.document_name,
                content=result.content,
                score=result.score,
                page_number=result.page_number,
                metadata=result.metadata,
                query=query
            )
            citations.append(citation)

            # 更新结果
            result.citation = citation
            enriched_results.append(result)

        return enriched_results, citations
