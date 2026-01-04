# ============================================================
# Presentation Service - Schemas Module
# ============================================================

from .presentation import (
    SlideImage,
    Slide,
    PresentationBase,
    PresentationCreate,
    PresentationUpdate,
    PresentationResponse,
    PresentationListResponse,
    GenerateConfig,
    PresentationGenerateRequest,
    RegenerateSlideRequest,
    ChangeThemeRequest,
    UpdateSlideRequest,
    AddSlideRequest,
    ExportResponse,
)

from .assistant import (
    IntentType,
    ParsedIntent,
    ChatMessage,
    ConversationContext,
    AssistantChatRequest,
    AssistantAction,
    AssistantChatResponse,
    ConfirmActionRequest,
    ConfirmActionResponse,
)

__all__ = [
    # Presentation schemas
    "SlideImage",
    "Slide",
    "PresentationBase",
    "PresentationCreate",
    "PresentationUpdate",
    "PresentationResponse",
    "PresentationListResponse",
    "GenerateConfig",
    "PresentationGenerateRequest",
    "RegenerateSlideRequest",
    "ChangeThemeRequest",
    "UpdateSlideRequest",
    "AddSlideRequest",
    "ExportResponse",
    # Assistant schemas
    "IntentType",
    "ParsedIntent",
    "ChatMessage",
    "ConversationContext",
    "AssistantChatRequest",
    "AssistantAction",
    "AssistantChatResponse",
    "ConfirmActionRequest",
    "ConfirmActionResponse",
]
