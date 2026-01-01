# ============================================================
# Chunk Model (用于 BM25 索引 - PostgreSQL 备份)
# 主要数据存储在 Milvus 中
# ============================================================

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class Chunk(Base):
    """文档分块表 (BM25 索引备份)"""
    __tablename__ = "chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=True)
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Chunk {self.document_id}:{self.chunk_index}>"
