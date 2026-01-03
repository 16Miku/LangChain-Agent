# ============================================================
# Presentation Service - Presentation Schemas
# ============================================================

import uuid
from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field, ConfigDict


# ============================
# 幻灯片相关 Schema
# ============================

class SlideImage(BaseModel):
    """幻灯片图片"""
    url: str
    position: str = "right"  # left, right, top, bottom, background
    size: str = "medium"  # small, medium, large, full
    caption: Optional[str] = None


class Slide(BaseModel):
    """幻灯片数据模型"""
    title: str
    content: str  # 支持 Markdown
    layout: str = "bullet_points"
    background: Optional[str] = None
    notes: Optional[str] = None
    images: List[SlideImage] = []
    transition: str = "slide"


# ============================
# 演示文稿相关 Schema
# ============================

class PresentationBase(BaseModel):
    """演示文稿基础 Schema"""
    title: str = Field(..., min_length=1, max_length=255, description="演示文稿标题")
    description: Optional[str] = Field(None, description="演示文稿描述")
    theme: str = Field("modern_business", description="主题名称")
    target_audience: Optional[str] = Field("general", description="目标受众")
    presentation_type: Optional[str] = Field("informative", description="演示类型")
    include_images: bool = Field(True, description="是否包含图片")
    image_style: Optional[str] = Field("professional", description="图片风格")


class PresentationCreate(PresentationBase):
    """创建演示文稿"""
    slides: List[Slide] = []


class PresentationUpdate(BaseModel):
    """更新演示文稿"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    slides: Optional[List[Slide]] = None
    theme: Optional[str] = None
    custom_theme: Optional[Dict[str, Any]] = None
    layout_config: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class PresentationResponse(BaseModel):
    """演示文稿响应"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    slides: List[Slide]
    layout_config: Dict[str, Any] = {}
    theme: str
    custom_theme: Optional[Dict[str, Any]] = None
    target_audience: Optional[str] = None
    presentation_type: Optional[str] = None
    include_images: bool = True
    image_style: Optional[str] = None
    slide_count: int
    thumbnail: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime


class PresentationListResponse(BaseModel):
    """演示文稿列表响应"""
    presentations: List[PresentationResponse]
    total: int
    page: int
    page_size: int


# ============================
# 生成配置 Schema
# ============================

class GenerateConfig(BaseModel):
    """生成演示文稿的配置"""
    topic: str = Field(..., min_length=1, description="演示文稿主题")
    slide_count: int = Field(10, ge=3, le=50, description="幻灯片数量")
    target_audience: str = Field("general", description="目标受众")
    presentation_type: str = Field("informative", description="演示类型")
    theme: str = Field("modern_business", description="主题")
    include_images: bool = Field(True, description="是否包含图片")
    image_style: str = Field("professional", description="图片风格")
    language: str = Field("zh-CN", description="语言")


class PresentationGenerateRequest(GenerateConfig):
    """生成演示文稿请求"""
    title: Optional[str] = Field(None, description="自定义标题，默认使用主题")


# ============================
# 编辑操作 Schema
# ============================

class RegenerateSlideRequest(BaseModel):
    """重新生成幻灯片请求"""
    feedback: str = Field(..., min_length=1, description="修改反馈或新要求")


class ChangeThemeRequest(BaseModel):
    """更换主题请求"""
    theme: str = Field(..., description="新主题名称")


class UpdateSlideRequest(BaseModel):
    """更新幻灯片内容请求"""
    title: Optional[str] = None
    content: Optional[str] = None
    layout: Optional[str] = None
    background: Optional[str] = None
    notes: Optional[str] = None
    images: Optional[List[SlideImage]] = None


class AddSlideRequest(BaseModel):
    """添加幻灯片请求"""
    slide: Slide
    position: Optional[int] = Field(None, description="插入位置，默认添加到末尾")


# ============================
# 导出 Schema
# ============================

class ExportResponse(BaseModel):
    """导出响应"""
    content_type: str
    filename: str
    content: str  # Base64 编码的内容或 HTML 内容
