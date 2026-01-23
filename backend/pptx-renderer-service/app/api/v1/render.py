# ============================================================
# Render API - 渲染 API 端点
# ============================================================
"""
提供 HTML 到 PPTX 的渲染 API
"""

import base64
import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import io

from app.services.html_renderer import get_renderer_service, RenderResult
from app.services.pptx_generator import PptxGeneratorService
from app.services.position_extractor import ElementPosition

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================
# 请求/响应模型
# ============================================================


class SlideRenderRequest(BaseModel):
    """单页幻灯片渲染请求"""

    html: str = Field(..., description="幻灯片 HTML 内容")
    width: int = Field(default=1920, description="渲染宽度 (像素)")
    height: int = Field(default=1080, description="渲染高度 (像素)")
    use_screenshot_background: bool = Field(
        default=False,
        description="是否使用截图作为 PPTX 背景 (而非提取元素)"
    )


class MultiSlideRenderRequest(BaseModel):
    """多页幻灯片渲染请求"""

    slides: List[SlideRenderRequest] = Field(..., description="幻灯片列表")


class PreviewRequest(BaseModel):
    """预览请求"""

    html: str = Field(..., description="幻灯片 HTML 内容")
    width: int = Field(default=1920, description="渲染宽度")
    height: int = Field(default=1080, description="渲染高度")
    format: str = Field(default="png", description="图片格式 (png/jpeg)")
    quality: int = Field(default=95, description="JPEG 质量 (1-100)")


class ElementPositionResponse(BaseModel):
    """元素位置响应"""

    element_id: str
    element_type: str
    x: float
    y: float
    width: float
    height: float
    content: Optional[str] = None
    src: Optional[str] = None
    font_size: Optional[float] = None
    font_family: Optional[str] = None
    color: Optional[str] = None


class RenderResponse(BaseModel):
    """渲染响应"""

    success: bool
    message: str
    elements_count: int = 0
    elements: List[ElementPositionResponse] = []
    screenshot_base64: Optional[str] = None


class ExtractRequest(BaseModel):
    """元素提取请求"""

    html: str = Field(..., description="幻灯片 HTML 内容")
    width: int = Field(default=1920, description="渲染宽度")
    height: int = Field(default=1080, description="渲染高度")


# ============================================================
# API 端点
# ============================================================


@router.post("", response_class=StreamingResponse)
async def render_to_pptx(request: SlideRenderRequest):
    """
    渲染 HTML 幻灯片为 PPTX 文件

    - 接收幻灯片 HTML
    - 使用 Playwright 渲染并提取元素位置
    - 生成 PPTX 文件并返回

    Args:
        request: 渲染请求

    Returns:
        StreamingResponse: PPTX 文件流
    """
    try:
        # 获取渲染服务
        renderer = await get_renderer_service()

        # 渲染 HTML
        result: RenderResult = await renderer.render_slide(
            slide_html=request.html,
            width=request.width,
            height=request.height,
        )

        # 生成 PPTX
        generator = PptxGeneratorService()

        if request.use_screenshot_background:
            # 使用截图作为背景
            pptx_bytes = generator.generate(
                elements=[],
                screenshot=result.screenshot,
                render_width=request.width,
                render_height=request.height,
                use_screenshot_background=True,
            )
        else:
            # 使用提取的元素
            pptx_bytes = generator.generate(
                elements=result.elements,
                screenshot=result.screenshot,
                render_width=request.width,
                render_height=request.height,
                use_screenshot_background=False,
            )

        # 返回 PPTX 文件
        return StreamingResponse(
            io.BytesIO(pptx_bytes),
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={
                "Content-Disposition": "attachment; filename=presentation.pptx"
            }
        )

    except Exception as e:
        logger.error(f"渲染失败: {e}")
        raise HTTPException(status_code=500, detail=f"渲染失败: {str(e)}")


@router.post("/multi", response_class=StreamingResponse)
async def render_multi_slides_to_pptx(request: MultiSlideRenderRequest):
    """
    渲染多页幻灯片为 PPTX 文件

    Args:
        request: 多页渲染请求

    Returns:
        StreamingResponse: PPTX 文件流
    """
    try:
        renderer = await get_renderer_service()
        generator = PptxGeneratorService()

        slides_data = []

        for i, slide_req in enumerate(request.slides):
            logger.info(f"渲染幻灯片 {i + 1}/{len(request.slides)}")

            result = await renderer.render_slide(
                slide_html=slide_req.html,
                width=slide_req.width,
                height=slide_req.height,
            )

            slides_data.append({
                "elements": result.elements,
                "screenshot": result.screenshot,
                "use_screenshot_background": slide_req.use_screenshot_background,
            })

        # 生成多页 PPTX
        pptx_bytes = generator.generate_multi_slide(slides_data)

        return StreamingResponse(
            io.BytesIO(pptx_bytes),
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={
                "Content-Disposition": "attachment; filename=presentation.pptx"
            }
        )

    except Exception as e:
        logger.error(f"多页渲染失败: {e}")
        raise HTTPException(status_code=500, detail=f"渲染失败: {str(e)}")


@router.post("/preview")
async def render_preview(request: PreviewRequest):
    """
    渲染预览截图

    Args:
        request: 预览请求

    Returns:
        Response: 图片响应
    """
    try:
        renderer = await get_renderer_service()

        screenshot = await renderer.get_screenshot_only(
            slide_html=request.html,
            width=request.width,
            height=request.height,
            format=request.format,
            quality=request.quality,
        )

        media_type = "image/png" if request.format == "png" else "image/jpeg"

        return Response(
            content=screenshot,
            media_type=media_type,
            headers={
                "Content-Disposition": f"inline; filename=preview.{request.format}"
            }
        )

    except Exception as e:
        logger.error(f"预览渲染失败: {e}")
        raise HTTPException(status_code=500, detail=f"预览失败: {str(e)}")


@router.post("/preview/base64")
async def render_preview_base64(request: PreviewRequest) -> dict:
    """
    渲染预览截图并返回 base64 编码

    Args:
        request: 预览请求

    Returns:
        dict: 包含 base64 编码截图的响应
    """
    try:
        renderer = await get_renderer_service()

        screenshot = await renderer.get_screenshot_only(
            slide_html=request.html,
            width=request.width,
            height=request.height,
            format=request.format,
            quality=request.quality,
        )

        b64_data = base64.b64encode(screenshot).decode("utf-8")
        mime_type = "image/png" if request.format == "png" else "image/jpeg"

        return {
            "success": True,
            "data": f"data:{mime_type};base64,{b64_data}",
            "format": request.format,
            "width": request.width,
            "height": request.height,
        }

    except Exception as e:
        logger.error(f"预览渲染失败: {e}")
        raise HTTPException(status_code=500, detail=f"预览失败: {str(e)}")


@router.post("/extract")
async def extract_elements(request: ExtractRequest) -> RenderResponse:
    """
    提取 HTML 中的元素位置信息 (不生成 PPTX)

    Args:
        request: 提取请求

    Returns:
        RenderResponse: 元素位置信息
    """
    try:
        renderer = await get_renderer_service()

        result = await renderer.render_slide(
            slide_html=request.html,
            width=request.width,
            height=request.height,
        )

        # 转换元素为响应格式
        elements_response = [
            ElementPositionResponse(
                element_id=el.element_id,
                element_type=el.element_type,
                x=el.x,
                y=el.y,
                width=el.width,
                height=el.height,
                content=el.content,
                src=el.src,
                font_size=el.font_size,
                font_family=el.font_family,
                color=el.color,
            )
            for el in result.elements
        ]

        return RenderResponse(
            success=True,
            message=f"成功提取 {len(elements_response)} 个元素",
            elements_count=len(elements_response),
            elements=elements_response,
            screenshot_base64=base64.b64encode(result.screenshot).decode("utf-8"),
        )

    except Exception as e:
        logger.error(f"元素提取失败: {e}")
        raise HTTPException(status_code=500, detail=f"提取失败: {str(e)}")
