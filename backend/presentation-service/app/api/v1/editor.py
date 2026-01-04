# ============================================================
# Presentation Service - Editor API
# 高级编辑功能：AI 生成、换主题、重生成等
# ============================================================

import uuid
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_current_user_id
from app.database import get_db
from app.models import Presentation
from app.schemas import (
    PresentationGenerateRequest,
    PresentationResponse,
    RegenerateSlideRequest,
    ChangeThemeRequest,
    UpdateSlideRequest,
    AddSlideRequest,
    Slide,
)
from app.services.presentation_service import PresentationService

router = APIRouter(prefix="/editor", tags=["editor"])


@router.post("/generate", response_model=PresentationResponse)
async def generate_presentation(
    data: PresentationGenerateRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    AI 生成演示文稿
    根据主题和配置自动生成幻灯片内容
    """
    service = PresentationService(db)

    try:
        # 调用服务生成演示文稿
        presentation = await service.generate_presentation(
            user_id=user_id,
            topic=data.topic,
            slide_count=data.slide_count,
            target_audience=data.target_audience,
            presentation_type=data.presentation_type,
            theme=data.theme,
            include_images=data.include_images,
            image_style=data.image_style,
            language=data.language,
            custom_title=data.title,
        )

        return PresentationResponse(
            id=str(presentation.id),
            user_id=str(presentation.user_id),
            title=presentation.title,
            description=presentation.description,
            slides=presentation.slides,
            layout_config=presentation.layout_config or {},
            theme=presentation.theme,
            custom_theme=presentation.custom_theme,
            target_audience=presentation.target_audience,
            presentation_type=presentation.presentation_type,
            include_images=presentation.include_images,
            image_style=presentation.image_style,
            slide_count=presentation.slide_count,
            thumbnail=presentation.thumbnail,
            status=presentation.status,
            created_at=presentation.created_at,
            updated_at=presentation.updated_at,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate presentation: {str(e)}"
        )


@router.post("/{presentation_id}/regenerate/{slide_index}", response_model=PresentationResponse)
async def regenerate_slide(
    presentation_id: str,
    slide_index: int,
    data: RegenerateSlideRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    重新生成指定幻灯片
    根据用户反馈重新生成特定幻灯片的内容
    """
    try:
        p_id = uuid.UUID(presentation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid presentation ID"
        )

    # 检查权限并获取演示文稿
    result = await db.execute(
        select(Presentation).where(
            Presentation.id == p_id,
            Presentation.user_id == user_id
        )
    )
    presentation = result.scalar_one_or_none()

    if not presentation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presentation not found"
        )

    # 检查幻灯片索引
    if slide_index < 0 or slide_index >= len(presentation.slides):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid slide index. Must be between 0 and {len(presentation.slides) - 1}"
        )

    service = PresentationService(db)

    try:
        # 重新生成幻灯片
        updated_presentation = await service.regenerate_slide(
            presentation=presentation,
            slide_index=slide_index,
            feedback=data.feedback,
        )

        # 保存到数据库
        await db.commit()
        await db.refresh(updated_presentation)

        return PresentationResponse(
            id=str(updated_presentation.id),
            user_id=str(updated_presentation.user_id),
            title=updated_presentation.title,
            description=updated_presentation.description,
            slides=updated_presentation.slides,
            layout_config=updated_presentation.layout_config or {},
            theme=updated_presentation.theme,
            custom_theme=updated_presentation.custom_theme,
            target_audience=updated_presentation.target_audience,
            presentation_type=updated_presentation.presentation_type,
            include_images=updated_presentation.include_images,
            image_style=updated_presentation.image_style,
            slide_count=updated_presentation.slide_count,
            thumbnail=updated_presentation.thumbnail,
            status=updated_presentation.status,
            created_at=updated_presentation.created_at,
            updated_at=updated_presentation.updated_at,
        )

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to regenerate slide: {str(e)}"
        )


@router.post("/{presentation_id}/theme", response_model=PresentationResponse)
async def change_theme(
    presentation_id: str,
    data: ChangeThemeRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    更换演示文稿主题
    """
    try:
        p_id = uuid.UUID(presentation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid presentation ID"
        )

    result = await db.execute(
        select(Presentation).where(
            Presentation.id == p_id,
            Presentation.user_id == user_id
        )
    )
    presentation = result.scalar_one_or_none()

    if not presentation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presentation not found"
        )

    # 更新主题
    presentation.theme = data.theme
    await db.commit()
    await db.refresh(presentation)

    return PresentationResponse(
        id=str(presentation.id),
        user_id=str(presentation.user_id),
        title=presentation.title,
        description=presentation.description,
        slides=presentation.slides,
        layout_config=presentation.layout_config or {},
        theme=presentation.theme,
        custom_theme=presentation.custom_theme,
        target_audience=presentation.target_audience,
        presentation_type=presentation.presentation_type,
        include_images=presentation.include_images,
        image_style=presentation.image_style,
        slide_count=presentation.slide_count,
        thumbnail=presentation.thumbnail,
        status=presentation.status,
        created_at=presentation.created_at,
        updated_at=presentation.updated_at,
    )


@router.put("/{presentation_id}/slides/{slide_index}", response_model=PresentationResponse)
async def update_slide(
    presentation_id: str,
    slide_index: int,
    data: UpdateSlideRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    更新指定幻灯片内容
    """
    try:
        p_id = uuid.UUID(presentation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid presentation ID"
        )

    result = await db.execute(
        select(Presentation).where(
            Presentation.id == p_id,
            Presentation.user_id == user_id
        )
    )
    presentation = result.scalar_one_or_none()

    if not presentation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presentation not found"
        )

    # 检查索引
    if slide_index < 0 or slide_index >= len(presentation.slides):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid slide index"
        )

    # 更新幻灯片 - 需要创建新的 list 来触发 SQLAlchemy 检测变化
    slides = list(presentation.slides)  # 复制列表
    slide = dict(slides[slide_index])   # 复制字典

    if data.title is not None:
        slide["title"] = data.title
    if data.content is not None:
        slide["content"] = data.content
    if data.layout is not None:
        slide["layout"] = data.layout
    if data.background is not None:
        slide["background"] = data.background
    if data.notes is not None:
        slide["notes"] = data.notes
    if data.images is not None:
        slide["images"] = [img.model_dump() for img in data.images]

    slides[slide_index] = slide
    presentation.slides = slides  # 赋值新列表触发 SQLAlchemy 更新检测
    presentation.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(presentation)

    return PresentationResponse(
        id=str(presentation.id),
        user_id=str(presentation.user_id),
        title=presentation.title,
        description=presentation.description,
        slides=presentation.slides,
        layout_config=presentation.layout_config or {},
        theme=presentation.theme,
        custom_theme=presentation.custom_theme,
        target_audience=presentation.target_audience,
        presentation_type=presentation.presentation_type,
        include_images=presentation.include_images,
        image_style=presentation.image_style,
        slide_count=presentation.slide_count,
        thumbnail=presentation.thumbnail,
        status=presentation.status,
        created_at=presentation.created_at,
        updated_at=presentation.updated_at,
    )


@router.post("/{presentation_id}/slides", response_model=PresentationResponse)
async def add_slide(
    presentation_id: str,
    data: AddSlideRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    添加新幻灯片
    """
    try:
        p_id = uuid.UUID(presentation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid presentation ID"
        )

    result = await db.execute(
        select(Presentation).where(
            Presentation.id == p_id,
            Presentation.user_id == user_id
        )
    )
    presentation = result.scalar_one_or_none()

    if not presentation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presentation not found"
        )

    # 添加幻灯片
    slide_data = data.slide.model_dump()
    slides = list(presentation.slides)  # 复制列表

    if data.position is not None:
        if data.position < 0 or data.position > len(slides):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid position"
            )
        slides.insert(data.position, slide_data)
    else:
        slides.append(slide_data)

    presentation.slides = slides  # 赋值新列表触发 SQLAlchemy 更新检测
    presentation.slide_count = len(slides)
    presentation.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(presentation)

    return PresentationResponse(
        id=str(presentation.id),
        user_id=str(presentation.user_id),
        title=presentation.title,
        description=presentation.description,
        slides=presentation.slides,
        layout_config=presentation.layout_config or {},
        theme=presentation.theme,
        custom_theme=presentation.custom_theme,
        target_audience=presentation.target_audience,
        presentation_type=presentation.presentation_type,
        include_images=presentation.include_images,
        image_style=presentation.image_style,
        slide_count=presentation.slide_count,
        thumbnail=presentation.thumbnail,
        status=presentation.status,
        created_at=presentation.created_at,
        updated_at=presentation.updated_at,
    )


@router.delete("/{presentation_id}/slides/{slide_index}", response_model=PresentationResponse)
async def delete_slide(
    presentation_id: str,
    slide_index: int,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    删除指定幻灯片
    """
    try:
        p_id = uuid.UUID(presentation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid presentation ID"
        )

    result = await db.execute(
        select(Presentation).where(
            Presentation.id == p_id,
            Presentation.user_id == user_id
        )
    )
    presentation = result.scalar_one_or_none()

    if not presentation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presentation not found"
        )

    # 检查索引
    if slide_index < 0 or slide_index >= len(presentation.slides):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid slide index"
        )

    # 至少保留一个幻灯片
    if len(presentation.slides) <= 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete the last slide"
        )

    # 删除幻灯片 - 创建新列表触发 SQLAlchemy 检测
    slides = list(presentation.slides)
    slides.pop(slide_index)
    presentation.slides = slides
    presentation.slide_count = len(slides)
    presentation.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(presentation)

    return PresentationResponse(
        id=str(presentation.id),
        user_id=str(presentation.user_id),
        title=presentation.title,
        description=presentation.description,
        slides=presentation.slides,
        layout_config=presentation.layout_config or {},
        theme=presentation.theme,
        custom_theme=presentation.custom_theme,
        target_audience=presentation.target_audience,
        presentation_type=presentation.presentation_type,
        include_images=presentation.include_images,
        image_style=presentation.image_style,
        slide_count=presentation.slide_count,
        thumbnail=presentation.thumbnail,
        status=presentation.status,
        created_at=presentation.created_at,
        updated_at=presentation.updated_at,
    )
