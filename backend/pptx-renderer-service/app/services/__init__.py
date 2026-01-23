# ============================================================
# Services Package
# ============================================================
"""
服务层模块

包含:
- HtmlRendererService: HTML 渲染服务
- PositionExtractorService: 位置提取服务
- PptxGeneratorService: PPTX 生成服务
"""

from app.services.html_renderer import HtmlRendererService
from app.services.position_extractor import PositionExtractorService
from app.services.pptx_generator import PptxGeneratorService

__all__ = [
    "HtmlRendererService",
    "PositionExtractorService",
    "PptxGeneratorService",
]
