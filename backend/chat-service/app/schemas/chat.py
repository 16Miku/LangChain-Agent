# ============================================================
# Chat Service - Chat Request/Response Schemas
# ============================================================

from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Schema for chat request."""

    conversation_id: Optional[str] = Field(default=None, alias="conversationId")
    content: str
    images: Optional[List[str]] = None
    api_keys: Optional[Dict[str, str]] = Field(default=None, alias="apiKeys")

    class Config:
        populate_by_name = True


class ChatStreamEvent(BaseModel):
    """Schema for SSE stream event."""

    type: Literal["text", "tool_start", "tool_end", "citation", "done", "error"]
    data: Any
