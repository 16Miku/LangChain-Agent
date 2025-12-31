# ============================================================
# Chat Service - Chat Routes (Stream + Message Storage)
# ============================================================

from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user, CurrentUser
from app.schemas.chat import ChatRequest
from app.schemas.message import MessageCreate
from app.schemas.conversation import ConversationCreate
from app.services.conversation_service import ConversationService
from app.services.message_service import MessageService
from app.services.agent_service import chat_with_agent_stream


router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/stream")
async def stream_chat(
    request: ChatRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Stream chat response using Server-Sent Events (SSE).

    This endpoint:
    1. Creates a new conversation if conversation_id is not provided
    2. Saves the user message to the database
    3. Streams the AI response
    4. Saves the final AI response to the database

    SSE Events:
    - text: AI text response chunk (base64 encoded)
    - tool_start: Tool execution started (tool name)
    - tool_end: Tool execution completed (tool name + output)
    - done: Stream completed
    - error: Error occurred
    """
    conv_service = ConversationService(db)
    msg_service = MessageService(db)

    # Get or create conversation
    conversation_id = request.conversation_id

    if not conversation_id:
        # Create new conversation with first message as title
        title = request.content[:50] + "..." if len(request.content) > 50 else request.content
        conv_data = ConversationCreate(title=title)
        conversation = await conv_service.create(
            user_id=current_user.id,
            data=conv_data,
        )
        conversation_id = conversation.id
    else:
        # Verify conversation exists and belongs to user
        conversation = await conv_service.get_by_id(
            conversation_id=conversation_id,
            user_id=current_user.id,
        )
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )

    # Save user message
    user_msg_data = MessageCreate(
        role="user",
        content=request.content,
        images=request.images,
    )
    await msg_service.create(
        conversation_id=conversation_id,
        user_id=current_user.id,
        data=user_msg_data,
    )

    # Get conversation history for context
    history_messages = await msg_service.get_conversation_history(
        conversation_id=conversation_id,
        user_id=current_user.id,
    )

    # Convert to simple format for agent (include images for multimodal context)
    history = [
        {
            "role": msg.role,
            "content": msg.content,
            "images": msg.images,  # Include images for multimodal history
        }
        for msg in history_messages[:-1]  # Exclude the just-added user message
    ]

    async def generate_and_save():
        """Generate stream and save final response."""
        import base64
        import json

        full_response = ""
        tool_calls = []
        current_tool = None

        async for chunk in chat_with_agent_stream(
            message=request.content,
            user_id=current_user.id,
            conversation_id=conversation_id,
            history=history,
            images=request.images,
            api_keys=request.api_keys,
        ):
            yield chunk

            # Parse chunk to accumulate response
            if chunk.startswith("event: text"):
                lines = chunk.strip().split("\n")
                for line in lines:
                    if line.startswith("data: "):
                        encoded = line[6:]
                        try:
                            decoded = base64.b64decode(encoded).decode("utf-8")
                            full_response += decoded
                        except Exception:
                            pass

            elif chunk.startswith("event: tool_start"):
                lines = chunk.strip().split("\n")
                for line in lines:
                    if line.startswith("data: "):
                        encoded = line[6:]
                        try:
                            tool_name = base64.b64decode(encoded).decode("utf-8")
                            current_tool = {
                                "id": f"tool_{len(tool_calls)}",
                                "name": tool_name,
                                "args": {},
                                "status": "running",
                            }
                        except Exception:
                            pass

            elif chunk.startswith("event: tool_end"):
                lines = chunk.strip().split("\n")
                for line in lines:
                    if line.startswith("data: "):
                        encoded = line[6:]
                        try:
                            decoded = base64.b64decode(encoded).decode("utf-8")
                            tool_data = json.loads(decoded)
                            if current_tool:
                                current_tool["status"] = "success"
                                current_tool["output"] = tool_data.get("output", "")
                                tool_calls.append(current_tool)
                                current_tool = None
                        except Exception:
                            pass

            elif chunk.startswith("event: done"):
                # Save assistant message with accumulated response
                if full_response:
                    assistant_msg_data = MessageCreate(
                        role="assistant",
                        content=full_response,
                        tool_calls=tool_calls if tool_calls else None,
                    )
                    # Create a new session for the final save
                    from app.database import AsyncSessionLocal
                    async with AsyncSessionLocal() as save_db:
                        save_msg_service = MessageService(save_db)
                        await save_msg_service.create(
                            conversation_id=conversation_id,
                            user_id=current_user.id,
                            data=assistant_msg_data,
                        )
                        await save_db.commit()

    return StreamingResponse(
        generate_and_save(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "X-Conversation-Id": conversation_id,
        },
    )


@router.post("/stop")
async def stop_chat(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """
    Stop the current chat stream.

    Note: This is a placeholder. Actual stream cancellation is handled
    by the client closing the connection.
    """
    return {"status": "ok", "message": "Stream stop requested"}
