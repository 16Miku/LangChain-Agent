# ============================================================
# Presentation Service - Editor API
# 高级编辑功能：AI 生成、换主题、重生成等
# ============================================================

import uuid
from datetime import datetime
from typing import List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

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
from app.services.layout_engine import layout_engine, LayoutType, LayoutConfig, LAYOUT_CONFIGS
from app.services.image_service import image_service, ImageSearchResult, ImageSearchResponse
from app.services.theme_service import theme_service, ThemeType, ThemeConfig, THEME_CONFIGS

router = APIRouter(prefix="/editor", tags=["editor"])


# ============================================================
# 布局引擎 API
# ============================================================

class LayoutInfo(BaseModel):
    """布局信息响应"""
    type: str
    name: str
    description: str
    css_class: str
    supports_images: bool
    supports_charts: bool
    max_content_length: int
    recommended_for: List[str]


class LayoutListResponse(BaseModel):
    """布局列表响应"""
    layouts: List[LayoutInfo]
    total: int


class LayoutSuggestionRequest(BaseModel):
    """布局推荐请求"""
    content_type: str


class LayoutSuggestionResponse(BaseModel):
    """布局推荐响应"""
    suggested_layout: str
    layout_info: LayoutInfo


@router.get("/layouts", response_model=LayoutListResponse)
async def get_all_layouts():
    """
    获取所有可用布局类型
    返回 19 种布局的详细信息
    """
    layouts = []
    for layout_type, config in LAYOUT_CONFIGS.items():
        layouts.append(LayoutInfo(
            type=layout_type,
            name=config.name,
            description=config.description,
            css_class=config.css_class,
            supports_images=config.supports_images,
            supports_charts=config.supports_charts,
            max_content_length=config.max_content_length,
            recommended_for=config.recommended_for,
        ))

    return LayoutListResponse(
        layouts=layouts,
        total=len(layouts)
    )


@router.get("/layouts/{layout_type}", response_model=LayoutInfo)
async def get_layout(layout_type: str):
    """
    获取指定布局的详细信息
    """
    config = layout_engine.get_layout(layout_type)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Layout type '{layout_type}' not found"
        )

    return LayoutInfo(
        type=layout_type,
        name=config.name,
        description=config.description,
        css_class=config.css_class,
        supports_images=config.supports_images,
        supports_charts=config.supports_charts,
        max_content_length=config.max_content_length,
        recommended_for=config.recommended_for,
    )


@router.post("/layouts/suggest", response_model=LayoutSuggestionResponse)
async def suggest_layout(request: LayoutSuggestionRequest):
    """
    根据内容类型推荐布局

    支持的内容类型:
    - opening, intro: 封面页
    - section, chapter: 章节页
    - content, points, features: 列表页
    - comparison, vs: 对比布局
    - chart, data, statistics: 图表布局
    - timeline, history, evolution: 时间线
    - process, workflow, steps: 流程图
    - quote, highlight: 引用页
    - kpi, metrics, numbers: 指标卡片
    - gallery, portfolio: 图片画廊
    - ending, thanks, qa: 结尾页
    - contact, social: 联系方式
    """
    suggested = layout_engine.suggest_layout(request.content_type)
    config = LAYOUT_CONFIGS[suggested]

    return LayoutSuggestionResponse(
        suggested_layout=suggested,
        layout_info=LayoutInfo(
            type=suggested,
            name=config.name,
            description=config.description,
            css_class=config.css_class,
            supports_images=config.supports_images,
            supports_charts=config.supports_charts,
            max_content_length=config.max_content_length,
            recommended_for=config.recommended_for,
        )
    )


@router.get("/layouts/css/{theme}")
async def get_layout_css(theme: str = "modern_business"):
    """
    获取布局的 CSS 样式

    Args:
        theme: 主题名称，默认 modern_business

    Returns:
        CSS 样式字符串
    """
    css = layout_engine.generate_layout_css(theme)
    return {"css": css, "theme": theme}


# ============================================================
# 图片服务 API
# ============================================================

class ImageSearchRequest(BaseModel):
    """图片搜索请求"""
    query: str
    per_page: int = 10
    page: int = 1
    orientation: str = "landscape"  # landscape, portrait, squarish


class ImageSuggestRequest(BaseModel):
    """图片关键词推荐请求"""
    title: str
    content: str = ""
    layout: str = "bullet_points"


class ImageSuggestResponse(BaseModel):
    """图片关键词推荐响应"""
    keywords: List[str]


@router.post("/images/search")
async def search_images(request: ImageSearchRequest):
    """
    搜索图片

    支持中英文关键词，自动翻译
    无需 API Key 也可使用 (使用 Unsplash Source)
    """
    result = await image_service.search_images(
        query=request.query,
        per_page=request.per_page,
        page=request.page,
        orientation=request.orientation,
    )
    return result


@router.get("/images/random")
async def get_random_image(
    query: str = None,
    orientation: str = "landscape",
):
    """
    获取随机图片

    Args:
        query: 可选关键词
        orientation: 图片方向
    """
    result = await image_service.get_random_image(
        query=query,
        orientation=orientation,
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get random image"
        )
    return result


@router.get("/images/for-content")
async def get_image_for_content(
    content_type: str,
    topic: str = None,
):
    """
    根据内容类型获取合适的图片 URL

    Args:
        content_type: 内容类型 (cover, section, data, timeline, etc.)
        topic: 主题关键词 (可选)
    """
    url = image_service.get_image_for_content(
        content_type=content_type,
        topic=topic,
    )
    return {"url": url, "content_type": content_type, "topic": topic}


@router.post("/images/suggest-keywords", response_model=ImageSuggestResponse)
async def suggest_image_keywords(request: ImageSuggestRequest):
    """
    为幻灯片推荐图片关键词

    根据标题、内容和布局类型推荐合适的图片搜索关键词
    """
    keywords = image_service.suggest_keywords_for_slide(
        title=request.title,
        content=request.content,
        layout=request.layout,
    )
    return ImageSuggestResponse(keywords=keywords)


# ============================================================
# 高级主题系统 API
# ============================================================

class ThemeInfo(BaseModel):
    """主题信息响应"""
    type: str
    name: str
    name_en: str
    description: str
    style: str
    recommended_for: List[str]
    preview_gradient: str


class ThemeColorsInfo(BaseModel):
    """主题颜色信息"""
    primary: str
    secondary: str
    accent: str
    background: str
    surface: str
    text_primary: str
    text_secondary: str
    border: str


class ThemeFontsInfo(BaseModel):
    """主题字体信息"""
    title: str
    subtitle: str
    body: str
    code: str


class ThemeDetailResponse(BaseModel):
    """主题详细响应"""
    type: str
    name: str
    name_en: str
    description: str
    colors: ThemeColorsInfo
    fonts: ThemeFontsInfo
    style: str
    recommended_for: List[str]
    preview_gradient: str


class ThemeListResponse(BaseModel):
    """主题列表响应"""
    themes: List[ThemeInfo]
    total: int


class ThemeSuggestRequest(BaseModel):
    """主题推荐请求"""
    scenario: str


class ThemeSuggestResponse(BaseModel):
    """主题推荐响应"""
    suggested_theme: str
    theme_info: ThemeInfo
    alternatives: List[str]


@router.get("/themes", response_model=ThemeListResponse)
async def get_all_themes():
    """
    获取所有可用主题

    返回 12 种精品主题的基本信息
    """
    themes = []
    for theme_type, config in THEME_CONFIGS.items():
        themes.append(ThemeInfo(
            type=theme_type,
            name=config.name,
            name_en=config.name_en,
            description=config.description,
            style=config.style,
            recommended_for=config.recommended_for,
            preview_gradient=config.preview_gradient,
        ))

    return ThemeListResponse(
        themes=themes,
        total=len(themes)
    )


@router.get("/themes/{theme_type}", response_model=ThemeDetailResponse)
async def get_theme(theme_type: str):
    """
    获取指定主题的详细信息

    包括颜色配置和字体配置
    """
    config = theme_service.get_theme(theme_type)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Theme '{theme_type}' not found"
        )

    return ThemeDetailResponse(
        type=theme_type,
        name=config.name,
        name_en=config.name_en,
        description=config.description,
        colors=ThemeColorsInfo(
            primary=config.colors.primary,
            secondary=config.colors.secondary,
            accent=config.colors.accent,
            background=config.colors.background,
            surface=config.colors.surface,
            text_primary=config.colors.text_primary,
            text_secondary=config.colors.text_secondary,
            border=config.colors.border,
        ),
        fonts=ThemeFontsInfo(
            title=config.fonts.title,
            subtitle=config.fonts.subtitle,
            body=config.fonts.body,
            code=config.fonts.code,
        ),
        style=config.style,
        recommended_for=config.recommended_for,
        preview_gradient=config.preview_gradient,
    )


@router.post("/themes/suggest", response_model=ThemeSuggestResponse)
async def suggest_theme(request: ThemeSuggestRequest):
    """
    根据场景推荐主题

    支持的场景关键词:
    - 商务/企业/正式 → 企业蓝
    - 科技/AI/人工智能 → 科技深色
    - 游戏/电竞 → 霓虹未来
    - 高端/奢华 → 典雅深色
    - 简洁/简约 → 极简白
    - 环保/健康 → 自然绿
    - 女性/儿童 → 柔和粉彩
    - 创意/营销 → 创意多彩
    - 学术/论文/教育 → 学术经典
    - 时尚 → 渐变紫
    - 旅游/美食 → 暖阳落日
    """
    suggested = theme_service.suggest_theme(request.scenario)
    config = THEME_CONFIGS[suggested]

    # 获取备选主题
    alternatives = theme_service.get_themes_for_scenario(request.scenario)
    alternatives = [t for t in alternatives if t != suggested][:3]

    return ThemeSuggestResponse(
        suggested_theme=suggested,
        theme_info=ThemeInfo(
            type=suggested,
            name=config.name,
            name_en=config.name_en,
            description=config.description,
            style=config.style,
            recommended_for=config.recommended_for,
            preview_gradient=config.preview_gradient,
        ),
        alternatives=alternatives,
    )


@router.get("/themes/{theme_type}/css")
async def get_theme_css(theme_type: str):
    """
    获取主题的 CSS 变量

    返回可直接使用的 CSS 样式
    """
    if not theme_service.validate_theme(theme_type):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Theme '{theme_type}' not found"
        )

    css = theme_service.generate_theme_css(theme_type)
    return {"css": css, "theme": theme_type}


@router.get("/themes/{theme_type}/reveal-css")
async def get_theme_reveal_css(theme_type: str):
    """
    获取 Reveal.js 演示文稿的主题 CSS

    返回适用于 Reveal.js 的完整主题样式
    """
    if not theme_service.validate_theme(theme_type):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Theme '{theme_type}' not found"
        )

    css = theme_service.generate_reveal_theme_css(theme_type)
    return {"css": css, "theme": theme_type}


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
    # 验证 ID 格式
    try:
        uuid.UUID(presentation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid presentation ID"
        )

    # 检查权限并获取演示文稿（使用字符串查询）
    result = await db.execute(
        select(Presentation).where(
            Presentation.id == presentation_id,
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
    # 验证 ID 格式
    try:
        uuid.UUID(presentation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid presentation ID"
        )

    # 使用字符串查询
    result = await db.execute(
        select(Presentation).where(
            Presentation.id == presentation_id,
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
    # 验证 ID 格式
    try:
        uuid.UUID(presentation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid presentation ID"
        )

    # 使用字符串查询
    result = await db.execute(
        select(Presentation).where(
            Presentation.id == presentation_id,
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
    # 验证 ID 格式
    try:
        uuid.UUID(presentation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid presentation ID"
        )

    # 使用字符串查询
    result = await db.execute(
        select(Presentation).where(
            Presentation.id == presentation_id,
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
    # 验证 ID 格式
    try:
        uuid.UUID(presentation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid presentation ID"
        )

    # 使用字符串查询
    result = await db.execute(
        select(Presentation).where(
            Presentation.id == presentation_id,
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
