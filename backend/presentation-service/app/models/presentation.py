# ============================================================
# Presentation Service - Presentation Model
# ============================================================

import json
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, JSON
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """SQLAlchemy Base 类"""
    pass


class Presentation(Base):
    """
    演示文稿数据模型
    """
    __tablename__ = "presentations"

    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # 用户关联
    user_id = Column(String(36), nullable=False, index=True)

    # 基本信息
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # 核心内容 (JSONB)
    slides = Column(JSON, nullable=False, default=list)
    layout_config = Column(JSON, nullable=False, default=dict)

    # 样式配置
    theme = Column(String(50), nullable=False, default="modern_business")
    custom_theme = Column(JSON, nullable=True)

    # 生成配置
    target_audience = Column(String(100), nullable=True)
    presentation_type = Column(String(50), nullable=True)  # informative, persuasive, instructional
    include_images = Column(Boolean, nullable=False, default=True)
    image_style = Column(String(50), nullable=True)

    # 元数据
    slide_count = Column(Integer, nullable=False, default=0)
    thumbnail = Column(Text, nullable=True)  # Base64 编码的预览图

    # 状态
    status = Column(String(20), nullable=False, default="draft")  # draft, completed, archived

    # 时间戳
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "title": self.title,
            "description": self.description,
            "slides": self.slides,
            "layout_config": self.layout_config,
            "theme": self.theme,
            "custom_theme": self.custom_theme,
            "target_audience": self.target_audience,
            "presentation_type": self.presentation_type,
            "include_images": self.include_images,
            "image_style": self.image_style,
            "slide_count": self.slide_count,
            "thumbnail": self.thumbnail,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class SlideVersion(Base):
    """
    幻灯片版本模型
    用于版本管理和回滚
    """
    __tablename__ = "slide_versions"

    # 主键
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # 关联演示文稿
    presentation_id = Column(String(36), nullable=False, index=True)

    # 幻灯片信息
    slide_index = Column(Integer, nullable=False)
    content = Column(JSON, nullable=False)
    layout = Column(String(50), nullable=True)

    # 版本号
    version_number = Column(Integer, nullable=False, default=1)

    # 时间戳
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": str(self.id),
            "presentation_id": str(self.presentation_id),
            "slide_index": self.slide_index,
            "content": self.content,
            "layout": self.layout,
            "version_number": self.version_number,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
