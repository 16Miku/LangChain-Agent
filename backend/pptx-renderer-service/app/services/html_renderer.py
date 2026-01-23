# ============================================================
# HTML Renderer Service - HTML 渲染服务
# ============================================================
"""
使用 Playwright 渲染 HTML 幻灯片并截图
"""

import asyncio
import base64
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from playwright.async_api import async_playwright, Browser, Page, Playwright

from app.config import settings
from app.services.position_extractor import PositionExtractorService, ElementPosition

logger = logging.getLogger(__name__)


@dataclass
class RenderResult:
    """渲染结果"""

    screenshot: bytes  # PNG 截图
    elements: List[ElementPosition]  # 元素位置列表
    metadata: Dict[str, Any]  # 幻灯片元数据
    width: int
    height: int

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典 (截图转为 base64)"""
        return {
            "screenshot_base64": base64.b64encode(self.screenshot).decode("utf-8"),
            "elements": [el.to_dict() for el in self.elements],
            "metadata": self.metadata,
            "width": self.width,
            "height": self.height,
        }


class HtmlRendererService:
    """
    HTML 渲染服务

    使用 Playwright 渲染 HTML 幻灯片，提取元素位置并生成截图。
    """

    def __init__(self):
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._position_extractor = PositionExtractorService()
        self._lock = asyncio.Lock()

    async def _ensure_browser(self) -> Browser:
        """
        确保浏览器已启动

        Returns:
            Browser: Playwright 浏览器实例
        """
        async with self._lock:
            if self._browser is None or not self._browser.is_connected():
                logger.info("启动 Playwright 浏览器...")
                self._playwright = await async_playwright().start()
                self._browser = await self._playwright.chromium.launch(
                    headless=settings.PLAYWRIGHT_HEADLESS,
                )
                logger.info("Playwright 浏览器启动成功")
            return self._browser

    async def close(self):
        """关闭浏览器和 Playwright"""
        async with self._lock:
            if self._browser:
                await self._browser.close()
                self._browser = None
            if self._playwright:
                await self._playwright.stop()
                self._playwright = None
            logger.info("Playwright 浏览器已关闭")

    async def render_slide(
        self,
        slide_html: str,
        width: int = None,
        height: int = None,
        wait_for_selector: Optional[str] = None,
        wait_timeout: int = None,
    ) -> RenderResult:
        """
        渲染 HTML 幻灯片

        Args:
            slide_html: 幻灯片 HTML 内容
            width: 视口宽度 (默认 1920)
            height: 视口高度 (默认 1080)
            wait_for_selector: 等待特定选择器出现
            wait_timeout: 等待超时时间 (毫秒)

        Returns:
            RenderResult: 包含截图和元素位置的渲染结果
        """
        width = width or settings.DEFAULT_SLIDE_WIDTH
        height = height or settings.DEFAULT_SLIDE_HEIGHT
        wait_timeout = wait_timeout or settings.PLAYWRIGHT_TIMEOUT

        browser = await self._ensure_browser()
        page: Optional[Page] = None

        try:
            # 创建新页面
            page = await browser.new_page(
                viewport={"width": width, "height": height},
                device_scale_factor=2,  # 高清截图
            )

            # 设置 HTML 内容
            await page.set_content(
                self._wrap_html(slide_html, width, height),
                wait_until="networkidle",
                timeout=wait_timeout,
            )

            # 等待特定选择器 (如果指定)
            if wait_for_selector:
                await page.wait_for_selector(
                    wait_for_selector,
                    timeout=wait_timeout,
                )

            # 等待字体和图片加载
            await self._wait_for_resources(page)

            # 提取元素位置
            elements = await self._position_extractor.extract_positions(page)

            # 提取幻灯片元数据
            metadata = await self._position_extractor.extract_slide_metadata(page)

            # 截图
            screenshot = await page.screenshot(
                type="png",
                full_page=False,
                clip={"x": 0, "y": 0, "width": width, "height": height},
            )

            logger.info(f"渲染完成: {width}x{height}, {len(elements)} 个元素")

            return RenderResult(
                screenshot=screenshot,
                elements=elements,
                metadata=metadata,
                width=width,
                height=height,
            )

        except Exception as e:
            logger.error(f"渲染幻灯片失败: {e}")
            raise

        finally:
            if page:
                await page.close()

    async def render_multiple_slides(
        self,
        slides_html: List[str],
        width: int = None,
        height: int = None,
    ) -> List[RenderResult]:
        """
        批量渲染多个幻灯片

        Args:
            slides_html: 幻灯片 HTML 列表
            width: 视口宽度
            height: 视口高度

        Returns:
            List[RenderResult]: 渲染结果列表
        """
        results = []
        for i, html in enumerate(slides_html):
            logger.info(f"渲染幻灯片 {i + 1}/{len(slides_html)}")
            result = await self.render_slide(html, width, height)
            results.append(result)
        return results

    async def get_screenshot_only(
        self,
        slide_html: str,
        width: int = None,
        height: int = None,
        format: str = "png",
        quality: int = None,
    ) -> bytes:
        """
        仅获取截图 (不提取元素位置)

        Args:
            slide_html: 幻灯片 HTML 内容
            width: 视口宽度
            height: 视口高度
            format: 图片格式 (png/jpeg)
            quality: JPEG 质量 (1-100)

        Returns:
            bytes: 截图数据
        """
        width = width or settings.DEFAULT_SLIDE_WIDTH
        height = height or settings.DEFAULT_SLIDE_HEIGHT
        quality = quality or settings.SCREENSHOT_QUALITY

        browser = await self._ensure_browser()
        page: Optional[Page] = None

        try:
            page = await browser.new_page(
                viewport={"width": width, "height": height},
                device_scale_factor=2,
            )

            await page.set_content(
                self._wrap_html(slide_html, width, height),
                wait_until="networkidle",
            )

            await self._wait_for_resources(page)

            screenshot_options = {
                "type": format,
                "full_page": False,
                "clip": {"x": 0, "y": 0, "width": width, "height": height},
            }

            if format == "jpeg":
                screenshot_options["quality"] = quality

            return await page.screenshot(**screenshot_options)

        finally:
            if page:
                await page.close()

    def _wrap_html(self, html: str, width: int, height: int) -> str:
        """
        包装 HTML 内容，添加必要的样式

        Args:
            html: 原始 HTML
            width: 视口宽度
            height: 视口高度

        Returns:
            str: 包装后的完整 HTML
        """
        # 检查是否已经是完整的 HTML 文档
        if "<html" in html.lower() or "<!doctype" in html.lower():
            return html

        # 包装为完整的 HTML 文档
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width={width}, height={height}">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        html, body {{
            width: {width}px;
            height: {height}px;
            overflow: hidden;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
                         'Helvetica Neue', Arial, sans-serif;
        }}
        body {{
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        [data-pptx-slide] {{
            width: {width}px;
            height: {height}px;
            position: relative;
            overflow: hidden;
        }}
    </style>
</head>
<body>
    {html}
</body>
</html>
"""

    async def _wait_for_resources(self, page: Page, timeout: int = 5000):
        """
        等待页面资源加载完成

        Args:
            page: Playwright Page 对象
            timeout: 超时时间 (毫秒)
        """
        try:
            # 等待所有图片加载
            await page.evaluate("""
            () => {
                return Promise.all(
                    Array.from(document.images)
                        .filter(img => !img.complete)
                        .map(img => new Promise((resolve, reject) => {
                            img.onload = resolve;
                            img.onerror = resolve; // 即使失败也继续
                            setTimeout(resolve, 5000); // 5秒超时
                        }))
                );
            }
            """)

            # 等待字体加载
            await page.evaluate("() => document.fonts.ready")

            # 短暂等待渲染完成
            await asyncio.sleep(0.1)

        except Exception as e:
            logger.warning(f"等待资源加载时出错: {e}")


# 全局服务实例
_renderer_service: Optional[HtmlRendererService] = None


async def get_renderer_service() -> HtmlRendererService:
    """获取渲染服务单例"""
    global _renderer_service
    if _renderer_service is None:
        _renderer_service = HtmlRendererService()
    return _renderer_service


async def close_renderer_service():
    """关闭渲染服务"""
    global _renderer_service
    if _renderer_service:
        await _renderer_service.close()
        _renderer_service = None
