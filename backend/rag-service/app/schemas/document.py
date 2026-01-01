# ============================================================
# Document Schemas
# ============================================================

from typing import Optional, List, Union
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


class DocumentCreate(BaseModel):
    """创建文档请求"""
    filename: str
    file_type: Optional[str] = None
    parse_method: str = Field(default="default", description="解析方法: default, mineru")


class DocumentResponse(BaseModel):
    """文档响应"""
    id: UUID
    user_id: Union[UUID, str]  # 兼容测试模式字符串 ID
    filename: str
    file_type: Optional[str]
    file_size: Optional[int]
    chunk_count: int
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """文档列表响应"""
    total: int
    documents: List[DocumentResponse]


class DocumentStatusResponse(BaseModel):
    """文档状态响应"""
    id: UUID
    filename: str
    status: str
    chunk_count: int
    error_message: Optional[str] = None
    estimated_time: Optional[int] = None  # 预计剩余处理时间（秒）


class DocumentUploadResponse(BaseModel):
    """文档上传响应"""
    document_id: UUID
    filename: str
    status: str
    estimated_time: Optional[int] = None
