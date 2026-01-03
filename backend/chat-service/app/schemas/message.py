# ============================================================
# Chat Service - Message Schemas
# ============================================================

from datetime import datetime
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    """Schema for tool call information."""

    id: str
    name: str
    args: Dict[str, Any] = Field(default_factory=dict)
    status: Literal["running", "success", "error"] = "running"
    output: Optional[str] = None
    duration: Optional[float] = None


class Citation(BaseModel):
    """Schema for citation/reference information from RAG."""

    chunk_id: str = Field(default="", alias="chunkId")
    document_id: str = Field(default="", alias="documentId")
    document_name: str = Field(default="", alias="documentName")
    page_number: Optional[int] = Field(default=None, alias="pageNumber")
    section: Optional[str] = None
    content: str = ""
    content_preview: Optional[str] = Field(default=None, alias="contentPreview")
    score: float = 0

    class Config:
        populate_by_name = True


class MessageCreate(BaseModel):
    """Schema for creating a new message."""

    role: Literal["user", "assistant", "system"]
    content: str
    images: Optional[List[str]] = None
    tool_calls: Optional[List[Any]] = Field(default=None, alias="toolCalls")  # Accept ToolCall or dict
    citations: Optional[List[Any]] = None  # Accept Citation or dict

    class Config:
        populate_by_name = True


class MessageResponse(BaseModel):
    """Schema for message response."""

    id: str
    role: str
    content: str
    timestamp: datetime = Field(alias="created_at")
    images: Optional[List[str]] = None
    tool_calls: Optional[List[Dict[str, Any]]] = Field(default=None, alias="toolCalls")
    citations: Optional[List[Dict[str, Any]]] = None

    class Config:
        from_attributes = True
        populate_by_name = True

    @classmethod
    def from_orm_model(cls, message):
        """Convert ORM model to response schema with proper field mapping."""
        return cls(
            id=message.id,
            role=message.role,
            content=message.content,
            timestamp=message.created_at,
            images=message.images,
            tool_calls=message.tool_calls,
            citations=message.citations,
        )


class MessageListResponse(BaseModel):
    """Schema for paginated message list response."""

    messages: List[MessageResponse]
    total: int
