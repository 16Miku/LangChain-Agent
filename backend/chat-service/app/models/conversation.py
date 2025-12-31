# ============================================================
# Chat Service - Conversation Model
# ============================================================

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Conversation(Base):
    """Conversation model for storing chat sessions."""

    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True)
    title = Column(String(255), default="New Chat")
    model = Column(String(50), nullable=True)
    message_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to messages
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )

    def __repr__(self):
        return f"<Conversation(id={self.id}, title={self.title}, user_id={self.user_id})>"
