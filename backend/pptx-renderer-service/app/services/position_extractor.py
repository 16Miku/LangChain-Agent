# ============================================================
# Position Extractor Service - 位置提取服务
# ============================================================
"""
从 Playwright 页面中提取带有 [data-pptx-element] 属性的元素位置信息
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class ElementPosition:
    """元素位置信息"""

    # 元素标识
    element_id: str
    element_type: str  # text, image, shape, chart 等

    # 位置信息 (像素)
    x: float
    y: float
    width: float
    height: float

    # 内容信息
    content: Optional[str] = None
    src: Optional[str] = None  # 图片源

    # 样式信息
    font_size: Optional[float] = None
    font_family: Optional[str] = None
    font_weight: Optional[str] = None
    color: Optional[str] = None
    background_color: Optional[str] = None
    text_align: Optional[str] = None

    # 额外属性
    attributes: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


class PositionExtractorService:
    """
    位置提取服务

    从 Playwright 页面中提取所有带有 [data-pptx-element] 属性的元素，
    获取它们的位置、尺寸和样式信息。
    """

    # 支持的元素类型
    ELEMENT_TYPES = ["text", "title", "subtitle", "image", "shape", "chart", "list", "table"]

    async def extract_positions(self, page) -> List[ElementPosition]:
        """
        从页面提取所有 [data-pptx-element] 元素的位置

        Args:
            page: Playwright Page 对象

        Returns:
            List[ElementPosition]: 元素位置列表
        """
        try:
            # 执行 JavaScript 提取元素信息
            elements_data = await page.evaluate(self._get_extraction_script())

            # 转换为 ElementPosition 对象
            positions = []
            for data in elements_data:
                position = self._parse_element_data(data)
                if position:
                    positions.append(position)

            logger.info(f"成功提取 {len(positions)} 个元素位置")
            return positions

        except Exception as e:
            logger.error(f"提取元素位置失败: {e}")
            raise

    def _get_extraction_script(self) -> str:
        """
        获取用于提取元素信息的 JavaScript 脚本

        Returns:
            str: JavaScript 代码
        """
        return """
        () => {
            const elements = document.querySelectorAll('[data-pptx-element]');
            const results = [];

            elements.forEach((el, index) => {
                const rect = el.getBoundingClientRect();
                const styles = window.getComputedStyle(el);

                // 获取元素类型
                const elementType = el.getAttribute('data-pptx-element') || 'text';

                // 获取元素 ID
                const elementId = el.getAttribute('data-pptx-id') ||
                                  el.id ||
                                  `element-${index}`;

                // 获取内容
                let content = null;
                if (elementType === 'image') {
                    content = null;
                } else {
                    content = el.innerText || el.textContent || '';
                }

                // 获取图片源
                let src = null;
                if (elementType === 'image') {
                    src = el.getAttribute('src') ||
                          el.getAttribute('data-src') ||
                          el.style.backgroundImage?.replace(/url\\(['"]?([^'"\\)]+)['"]?\\)/, '$1');
                }

                // 收集所有 data-pptx-* 属性
                const attributes = {};
                for (const attr of el.attributes) {
                    if (attr.name.startsWith('data-pptx-')) {
                        const key = attr.name.replace('data-pptx-', '');
                        attributes[key] = attr.value;
                    }
                }

                results.push({
                    element_id: elementId,
                    element_type: elementType,
                    x: rect.left,
                    y: rect.top,
                    width: rect.width,
                    height: rect.height,
                    content: content,
                    src: src,
                    font_size: parseFloat(styles.fontSize) || null,
                    font_family: styles.fontFamily || null,
                    font_weight: styles.fontWeight || null,
                    color: styles.color || null,
                    background_color: styles.backgroundColor || null,
                    text_align: styles.textAlign || null,
                    attributes: attributes
                });
            });

            return results;
        }
        """

    def _parse_element_data(self, data: Dict[str, Any]) -> Optional[ElementPosition]:
        """
        解析元素数据为 ElementPosition 对象

        Args:
            data: 从 JavaScript 提取的原始数据

        Returns:
            Optional[ElementPosition]: 元素位置对象，解析失败返回 None
        """
        try:
            return ElementPosition(
                element_id=data.get("element_id", "unknown"),
                element_type=data.get("element_type", "text"),
                x=float(data.get("x", 0)),
                y=float(data.get("y", 0)),
                width=float(data.get("width", 0)),
                height=float(data.get("height", 0)),
                content=data.get("content"),
                src=data.get("src"),
                font_size=data.get("font_size"),
                font_family=data.get("font_family"),
                font_weight=data.get("font_weight"),
                color=data.get("color"),
                background_color=data.get("background_color"),
                text_align=data.get("text_align"),
                attributes=data.get("attributes"),
            )
        except Exception as e:
            logger.warning(f"解析元素数据失败: {e}, 数据: {data}")
            return None

    async def extract_slide_metadata(self, page) -> Dict[str, Any]:
        """
        提取幻灯片元数据

        Args:
            page: Playwright Page 对象

        Returns:
            Dict[str, Any]: 幻灯片元数据
        """
        try:
            metadata = await page.evaluate("""
            () => {
                const slide = document.querySelector('[data-pptx-slide]') || document.body;
                const styles = window.getComputedStyle(slide);

                return {
                    width: slide.offsetWidth || window.innerWidth,
                    height: slide.offsetHeight || window.innerHeight,
                    background_color: styles.backgroundColor,
                    background_image: styles.backgroundImage,
                    title: document.title || null
                };
            }
            """)
            return metadata
        except Exception as e:
            logger.error(f"提取幻灯片元数据失败: {e}")
            return {}
