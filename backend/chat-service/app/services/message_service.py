# ============================================================
# Chat Service - Message Service
# ============================================================

from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.message import Message
from app.models.conversation import Conversation
from app.schemas.message import MessageCreate


class MessageService:
    """Service for managing messages."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        conversation_id: str,
        user_id: str,
        data: MessageCreate,
    ) -> Optional[Message]:
        """
        Create a new message in a conversation.

        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user (for ownership check)
            data: Message creation data

        Returns:
            Created message if conversation exists and is owned by user, None otherwise
        """
        # Verify conversation ownership
        result = await self.db.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
        )
        conversation = result.scalar_one_or_none()
        if not conversation:
            return None

        # Create message
        # Handle both Pydantic models and raw dicts for tool_calls and citations
        tool_calls_data = None
        if data.tool_calls:
            tool_calls_data = [
                tc.model_dump() if hasattr(tc, 'model_dump') else tc
                for tc in data.tool_calls
            ]

        citations_data = None
        if data.citations:
            citations_data = [
                c.model_dump() if hasattr(c, 'model_dump') else c
                for c in data.citations
            ]

        message = Message(
            conversation_id=conversation_id,
            role=data.role,
            content=data.content,
            images=data.images,
            tool_calls=tool_calls_data,
            citations=citations_data,
        )
        self.db.add(message)

        # Update conversation message count
        conversation.message_count += 1

        await self.db.flush()
        await self.db.refresh(message)
        return message

    async def get_by_id(
        self, message_id: str, user_id: str
    ) -> Optional[Message]:
        """
        Get a message by ID.

        Args:
            message_id: ID of the message
            user_id: ID of the user (for ownership check via conversation)

        Returns:
            Message if found and owned by user, None otherwise
        """
        result = await self.db.execute(
            select(Message)
            .join(Conversation)
            .where(
                Message.id == message_id,
                Conversation.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_conversation(
        self, conversation_id: str, user_id: str, skip: int = 0, limit: int = 50
    ) -> Tuple[List[Message], int]:
        """
        List messages for a conversation with pagination.

        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user (for ownership check)
            skip: Number of messages to skip
            limit: Maximum number of messages to return

        Returns:
            Tuple of (messages list, total count)
        """
        # Verify conversation ownership
        conv_result = await self.db.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
        )
        conversation = conv_result.scalar_one_or_none()
        if not conversation:
            return [], 0

        # Get total count
        count_result = await self.db.execute(
            select(func.count(Message.id)).where(
                Message.conversation_id == conversation_id
            )
        )
        total = count_result.scalar_one()

        # Get paginated messages
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .offset(skip)
            .limit(limit)
        )
        messages = list(result.scalars().all())

        return messages, total

    async def get_conversation_history(
        self, conversation_id: str, user_id: str
    ) -> List[Message]:
        """
        Get all messages in a conversation (for agent context).

        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user (for ownership check)

        Returns:
            List of messages ordered by creation time
        """
        messages, _ = await self.list_by_conversation(
            conversation_id, user_id, skip=0, limit=1000
        )
        return messages

    async def delete_by_conversation(
        self, conversation_id: str, user_id: str
    ) -> bool:
        """
        Delete all messages in a conversation.

        This is typically called when deleting a conversation.

        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user (for ownership check)

        Returns:
            True if messages were deleted, False if conversation not found
        """
        # Verify conversation ownership
        conv_result = await self.db.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
        )
        conversation = conv_result.scalar_one_or_none()
        if not conversation:
            return False

        # Delete all messages
        result = await self.db.execute(
            select(Message).where(Message.conversation_id == conversation_id)
        )
        messages = result.scalars().all()
        for message in messages:
            await self.db.delete(message)

        await self.db.flush()
        return True
