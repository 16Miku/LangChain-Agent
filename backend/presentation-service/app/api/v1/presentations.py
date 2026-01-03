# ============================================================
# Presentation Service - Presentations API
# ============================================================

import uuid
import base64
from typing import List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_current_user_id
from app.database import get_db
from app.models import Presentation
from app.schemas import (
    PresentationCreate,
    PresentationUpdate,
    PresentationResponse,
    PresentationListResponse,
)

router = APIRouter(prefix="/presentations", tags=["presentations"])


@router.get("", response_model=PresentationListResponse)
async def list_presentations(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(20, ge=1, le=100, description="获取数量"),
    status_filter: str = Query(None, description="状态过滤"),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    获取用户的演示文稿列表
    """
    query = select(Presentation).where(Presentation.user_id == user_id)

    if status_filter:
        query = query.where(Presentation.status == status_filter)

    # 排序：最新创建的在前
    query = query.order_by(Presentation.created_at.desc())

    # 分页
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    presentations = result.scalars().all()

    # 获取总数
    count_query = select(Presentation).where(Presentation.user_id == user_id)
    if status_filter:
        count_query = count_query.where(Presentation.status == status_filter)
    count_result = await db.execute(count_query)
    total = len(count_result.scalars().all())

    # 转换为响应格式
    presentation_list = [
        PresentationResponse(
            id=str(p.id),
            user_id=str(p.user_id),
            title=p.title,
            description=p.description,
            slides=p.slides,
            layout_config=p.layout_config or {},
            theme=p.theme,
            custom_theme=p.custom_theme,
            target_audience=p.target_audience,
            presentation_type=p.presentation_type,
            include_images=p.include_images,
            image_style=p.image_style,
            slide_count=p.slide_count,
            thumbnail=p.thumbnail,
            status=p.status,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
        for p in presentations
    ]

    return PresentationListResponse(
        presentations=presentation_list,
        total=total,
        page=skip // limit + 1,
        page_size=limit,
    )


@router.post("", response_model=PresentationResponse, status_code=status.HTTP_201_CREATED)
async def create_presentation(
    data: PresentationCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    创建新演示文稿
    """
    slides_data = [slide.model_dump() for slide in data.slides]

    presentation = Presentation(
        user_id=user_id,
        title=data.title,
        description=data.description,
        slides=slides_data,
        theme=data.theme,
        target_audience=data.target_audience,
        presentation_type=data.presentation_type,
        include_images=data.include_images,
        image_style=data.image_style,
        slide_count=len(slides_data),
        status="draft",
    )

    db.add(presentation)
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


@router.get("/{presentation_id}", response_model=PresentationResponse)
async def get_presentation(
    presentation_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    获取演示文稿详情
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


@router.put("/{presentation_id}", response_model=PresentationResponse)
async def update_presentation(
    presentation_id: str,
    data: PresentationUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    更新演示文稿
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

    # 更新字段
    if data.title is not None:
        presentation.title = data.title
    if data.description is not None:
        presentation.description = data.description
    if data.slides is not None:
        slides_data = [slide.model_dump() for slide in data.slides]
        presentation.slides = slides_data
        presentation.slide_count = len(slides_data)
    if data.theme is not None:
        presentation.theme = data.theme
    if data.custom_theme is not None:
        presentation.custom_theme = data.custom_theme
    if data.layout_config is not None:
        presentation.layout_config = data.layout_config
    if data.status is not None:
        presentation.status = data.status

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


@router.delete("/{presentation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_presentation(
    presentation_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    删除演示文稿
    """
    try:
        p_id = uuid.UUID(presentation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid presentation ID"
        )

    result = await db.execute(
        delete(Presentation).where(
            Presentation.id == p_id,
            Presentation.user_id == user_id
        )
    )

    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presentation not found"
        )

    await db.commit()
