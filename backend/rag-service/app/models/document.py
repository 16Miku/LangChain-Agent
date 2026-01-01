# ============================================================
# Document Model (PostgreSQL)
# ============================================================

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
import enum

from app.database import Base


class DocumentStatus(str, enum.Enum):
    """文档处理状态"""
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


class Document(Base):
    """文档元数据表"""
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50))
    file_size = Column(Integer)
    file_path = Column(String(500))  # MinIO 路径
    milvus_collection = Column(String(100))
    chunk_count = Column(Integer, default=0)
    status = Column(
        Enum(DocumentStatus),
        default=DocumentStatus.PENDING
    )
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Document {self.filename}>"
