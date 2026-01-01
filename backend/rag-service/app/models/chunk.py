# ============================================================
# Chunk Model (用于 BM25 索引 - PostgreSQL/SQLite)
# 主要数据存储在 Milvus 中
# ============================================================

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, JSON

from app.database import Base


class Chunk(Base):
    """文档分块表 (BM25 索引备份)"""
    __tablename__ = "chunks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=True)
    extra_data = Column("extra_data", JSON, default=dict)  # 重命名 metadata -> extra_data
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Chunk {self.document_id}:{self.chunk_index}>"
