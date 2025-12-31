# ============================================================
# Chat Service - Conversation Schemas
# ============================================================

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ConversationCreate(BaseModel):
    """Schema for creating a new conversation."""

    title: Optional[str] = Field(default="New Chat", max_length=255)
    model: Optional[str] = Field(default=None, max_length=50)


class ConversationUpdate(BaseModel):
    """Schema for updating a conversation."""

    title: Optional[str] = Field(default=None, max_length=255)
    model: Optional[str] = Field(default=None, max_length=50)


class ConversationResponse(BaseModel):
    """Schema for conversation response."""

    id: str
    title: str
    model: Optional[str] = None
    message_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    """Schema for paginated conversation list response."""

    conversations: List[ConversationResponse]
    total: int
