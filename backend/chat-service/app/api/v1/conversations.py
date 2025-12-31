# ============================================================
# Chat Service - Conversation Routes
# ============================================================

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user, CurrentUser
from app.schemas.conversation import (
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
    ConversationListResponse,
)
from app.schemas.message import MessageListResponse, MessageResponse
from app.services.conversation_service import ConversationService
from app.services.message_service import MessageService


router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.get("", response_model=ConversationListResponse)
async def list_conversations(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
):
    """
    List all conversations for the current user.

    Returns paginated list of conversations ordered by last update time.
    """
    service = ConversationService(db)
    conversations, total = await service.list_by_user(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )

    return ConversationListResponse(
        conversations=[ConversationResponse.model_validate(c) for c in conversations],
        total=total,
    )


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    data: ConversationCreate,
):
    """
    Create a new conversation.
    """
    service = ConversationService(db)
    conversation = await service.create(
        user_id=current_user.id,
        data=data,
    )
    return ConversationResponse.model_validate(conversation)


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Get a specific conversation by ID.
    """
    service = ConversationService(db)
    conversation = await service.get_by_id(
        conversation_id=conversation_id,
        user_id=current_user.id,
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    return ConversationResponse.model_validate(conversation)


@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    data: ConversationUpdate,
):
    """
    Update a conversation.
    """
    service = ConversationService(db)
    conversation = await service.update(
        conversation_id=conversation_id,
        user_id=current_user.id,
        data=data,
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    return ConversationResponse.model_validate(conversation)


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Delete a conversation and all its messages.
    """
    service = ConversationService(db)
    deleted = await service.delete(
        conversation_id=conversation_id,
        user_id=current_user.id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )


@router.get("/{conversation_id}/messages", response_model=MessageListResponse)
async def get_conversation_messages(
    conversation_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
):
    """
    Get all messages in a conversation.

    Returns paginated list of messages ordered by creation time.
    """
    service = MessageService(db)
    messages, total = await service.list_by_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )

    return MessageListResponse(
        messages=[MessageResponse.from_orm_model(m) for m in messages],
        total=total,
    )
