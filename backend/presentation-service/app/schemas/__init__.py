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

__all__ = [
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
]
