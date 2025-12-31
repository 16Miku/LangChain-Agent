# ============================================================
# Chat Service - Message Model
# ============================================================

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.database import Base


class Message(Base):
    """Message model for storing individual messages in a conversation."""

    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(
        String(36),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    images = Column(JSON, nullable=True)  # List of base64 images
    tool_calls = Column(JSON, nullable=True)  # List of tool call records
    citations = Column(JSON, nullable=True)  # List of citations
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to conversation
    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, role={self.role}, conversation_id={self.conversation_id})>"
