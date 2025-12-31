# ============================================================
# Chat Service - Conversation Service
# ============================================================

from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete

from app.models.conversation import Conversation
from app.schemas.conversation import ConversationCreate, ConversationUpdate


class ConversationService:
    """Service for managing conversations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self, user_id: str, data: ConversationCreate
    ) -> Conversation:
        """
        Create a new conversation.

        Args:
            user_id: ID of the user creating the conversation
            data: Conversation creation data

        Returns:
            Created conversation
        """
        conversation = Conversation(
            user_id=user_id,
            title=data.title or "New Chat",
            model=data.model,
        )
        self.db.add(conversation)
        await self.db.flush()
        await self.db.refresh(conversation)
        return conversation

    async def get_by_id(
        self, conversation_id: str, user_id: str
    ) -> Optional[Conversation]:
        """
        Get a conversation by ID.

        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user (for ownership check)

        Returns:
            Conversation if found and owned by user, None otherwise
        """
        result = await self.db.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_user(
        self, user_id: str, skip: int = 0, limit: int = 20
    ) -> Tuple[List[Conversation], int]:
        """
        List conversations for a user with pagination.

        Args:
            user_id: ID of the user
            skip: Number of conversations to skip
            limit: Maximum number of conversations to return

        Returns:
            Tuple of (conversations list, total count)
        """
        # Get total count
        count_result = await self.db.execute(
            select(func.count(Conversation.id)).where(
                Conversation.user_id == user_id
            )
        )
        total = count_result.scalar_one()

        # Get paginated conversations
        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        conversations = list(result.scalars().all())

        return conversations, total

    async def update(
        self, conversation_id: str, user_id: str, data: ConversationUpdate
    ) -> Optional[Conversation]:
        """
        Update a conversation.

        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user (for ownership check)
            data: Update data

        Returns:
            Updated conversation if found and owned by user, None otherwise
        """
        conversation = await self.get_by_id(conversation_id, user_id)
        if not conversation:
            return None

        if data.title is not None:
            conversation.title = data.title
        if data.model is not None:
            conversation.model = data.model

        await self.db.flush()
        await self.db.refresh(conversation)
        return conversation

    async def delete(self, conversation_id: str, user_id: str) -> bool:
        """
        Delete a conversation.

        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user (for ownership check)

        Returns:
            True if deleted, False if not found or not owned
        """
        conversation = await self.get_by_id(conversation_id, user_id)
        if not conversation:
            return False

        await self.db.delete(conversation)
        await self.db.flush()
        return True

    async def increment_message_count(
        self, conversation_id: str, user_id: str
    ) -> Optional[Conversation]:
        """
        Increment the message count for a conversation.

        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user (for ownership check)

        Returns:
            Updated conversation if found, None otherwise
        """
        conversation = await self.get_by_id(conversation_id, user_id)
        if not conversation:
            return None

        conversation.message_count += 1
        await self.db.flush()
        await self.db.refresh(conversation)
        return conversation
