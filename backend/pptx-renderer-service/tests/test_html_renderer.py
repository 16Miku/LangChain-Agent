# ============================================================
# HTML Renderer Service Tests - HTML 渲染服务测试
# ============================================================
"""
测试 HTML 渲染服务的核心功能
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

# 测试用 HTML
SAMPLE_HTML = """
<div data-pptx-slide style="width: 1920px; height: 1080px; background: #ffffff;">
    <h1 data-pptx-element="title"
        data-pptx-id="title-1"
        style="position: absolute; left: 100px; top: 100px; font-size: 48px; color: #333333;">
        测试标题
    </h1>
    <p data-pptx-element="text"
       data-pptx-id="text-1"
       style="position: absolute; left: 100px; top: 200px; font-size: 24px; color: #666666;">
        这是测试文本内容
    </p>
    <img data-pptx-element="image"
         data-pptx-id="image-1"
         src="https://picsum.photos/400/300"
         style="position: absolute; left: 100px; top: 300px; width: 400px; height: 300px;">
    <div data-pptx-element="shape"
         data-pptx-id="shape-1"
         data-pptx-shape="rectangle"
         style="position: absolute; left: 600px; top: 300px; width: 200px; height: 150px; background: #4a90d9;">
    </div>
</div>
"""

MINIMAL_HTML = """
<div data-pptx-slide>
    <h1 data-pptx-element="title">简单标题</h1>
</div>
"""


class TestPositionExtractor:
    """位置提取服务测试"""

    def test_element_position_dataclass(self):
        """测试 ElementPosition 数据类"""
        from app.services.position_extractor import ElementPosition

        position = ElementPosition(
            element_id="test-1",
            element_type="text",
            x=100.0,
            y=200.0,
            width=300.0,
            height=50.0,
            content="测试内容",
            font_size=24.0,
            color="rgb(51, 51, 51)",
        )

        assert position.element_id == "test-1"
        assert position.element_type == "text"
        assert position.x == 100.0
        assert position.y == 200.0
        assert position.width == 300.0
        assert position.height == 50.0
        assert position.content == "测试内容"
        assert position.font_size == 24.0

    def test_element_position_to_dict(self):
        """测试 ElementPosition 转换为字典"""
        from app.services.position_extractor import ElementPosition

        position = ElementPosition(
            element_id="test-1",
            element_type="title",
            x=0,
            y=0,
            width=100,
            height=50,
        )

        result = position.to_dict()

        assert isinstance(result, dict)
        assert result["element_id"] == "test-1"
        assert result["element_type"] == "title"
        assert result["x"] == 0
        assert result["y"] == 0

    def test_extraction_script_generation(self):
        """测试 JavaScript 提取脚本生成"""
        from app.services.position_extractor import PositionExtractorService

        service = PositionExtractorService()
        script = service._get_extraction_script()

        assert isinstance(script, str)
        assert "data-pptx-element" in script
        assert "getBoundingClientRect" in script
        assert "getComputedStyle" in script

    def test_parse_element_data_valid(self):
        """测试解析有效的元素数据"""
        from app.services.position_extractor import PositionExtractorService

        service = PositionExtractorService()

        data = {
            "element_id": "title-1",
            "element_type": "title",
            "x": 100,
            "y": 200,
            "width": 500,
            "height": 60,
            "content": "测试标题",
            "font_size": 48,
            "color": "rgb(0, 0, 0)",
        }

        result = service._parse_element_data(data)

        assert result is not None
        assert result.element_id == "title-1"
        assert result.element_type == "title"
        assert result.x == 100.0
        assert result.content == "测试标题"

    def test_parse_element_data_missing_fields(self):
        """测试解析缺少字段的元素数据"""
        from app.services.position_extractor import PositionExtractorService

        service = PositionExtractorService()

        # 最小必需字段
        data = {
            "element_id": "test",
            "element_type": "text",
            "x": 0,
            "y": 0,
            "width": 100,
            "height": 50,
        }

        result = service._parse_element_data(data)

        assert result is not None
        assert result.content is None
        assert result.font_size is None


class TestPptxGenerator:
    """PPTX 生成服务测试"""

    def test_generator_initialization(self):
        """测试生成器初始化"""
        from app.services.pptx_generator import PptxGeneratorService

        generator = PptxGeneratorService()

        assert generator.slide_width_inches == 13.333
        assert generator.slide_height_inches == 7.5

    def test_generator_custom_size(self):
        """测试自定义尺寸"""
        from app.services.pptx_generator import PptxGeneratorService

        generator = PptxGeneratorService(
            slide_width_inches=10.0,
            slide_height_inches=7.5,
        )

        assert generator.slide_width_inches == 10.0
        assert generator.slide_height_inches == 7.5

    def test_parse_color_rgb(self):
        """测试解析 RGB 颜色"""
        from app.services.pptx_generator import PptxGeneratorService

        generator = PptxGeneratorService()

        # 测试 rgb 格式
        color = generator._parse_color("rgb(255, 128, 0)")
        assert color is not None
        assert color[0] == 255  # R
        assert color[1] == 128  # G
        assert color[2] == 0    # B

    def test_parse_color_rgba(self):
        """测试解析 RGBA 颜色"""
        from app.services.pptx_generator import PptxGeneratorService

        generator = PptxGeneratorService()

        color = generator._parse_color("rgba(100, 150, 200, 0.5)")
        assert color is not None
        assert color[0] == 100
        assert color[1] == 150
        assert color[2] == 200

    def test_parse_color_hex(self):
        """测试解析十六进制颜色"""
        from app.services.pptx_generator import PptxGeneratorService

        generator = PptxGeneratorService()

        color = generator._parse_color("#ff8800")
        assert color is not None
        assert color[0] == 255
        assert color[1] == 136
        assert color[2] == 0

    def test_parse_color_invalid(self):
        """测试解析无效颜色"""
        from app.services.pptx_generator import PptxGeneratorService

        generator = PptxGeneratorService()

        color = generator._parse_color("invalid-color")
        assert color is None

        color = generator._parse_color("")
        assert color is None

        color = generator._parse_color(None)
        assert color is None

    def test_generate_empty_elements(self):
        """测试生成空元素的 PPTX"""
        from app.services.pptx_generator import PptxGeneratorService

        generator = PptxGeneratorService()
        pptx_bytes = generator.generate(elements=[])

        assert isinstance(pptx_bytes, bytes)
        assert len(pptx_bytes) > 0

        # 验证是有效的 PPTX 文件 (ZIP 格式)
        assert pptx_bytes[:4] == b'PK\x03\x04'

    def test_generate_with_text_element(self):
        """测试生成包含文本元素的 PPTX"""
        from app.services.pptx_generator import PptxGeneratorService
        from app.services.position_extractor import ElementPosition

        generator = PptxGeneratorService()

        elements = [
            ElementPosition(
                element_id="title-1",
                element_type="title",
                x=100,
                y=100,
                width=800,
                height=60,
                content="测试标题",
                font_size=48,
                color="rgb(0, 0, 0)",
            ),
            ElementPosition(
                element_id="text-1",
                element_type="text",
                x=100,
                y=200,
                width=600,
                height=100,
                content="这是测试文本内容",
                font_size=24,
                color="rgb(51, 51, 51)",
            ),
        ]

        pptx_bytes = generator.generate(elements=elements)

        assert isinstance(pptx_bytes, bytes)
        assert len(pptx_bytes) > 0
        assert pptx_bytes[:4] == b'PK\x03\x04'

    def test_generate_with_screenshot_background(self):
        """测试使用截图作为背景"""
        from app.services.pptx_generator import PptxGeneratorService
        from PIL import Image
        import io

        generator = PptxGeneratorService()

        # 创建测试图片
        img = Image.new('RGB', (1920, 1080), color='blue')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        screenshot = img_bytes.getvalue()

        pptx_bytes = generator.generate(
            elements=[],
            screenshot=screenshot,
            use_screenshot_background=True,
        )

        assert isinstance(pptx_bytes, bytes)
        assert len(pptx_bytes) > 0

    def test_convert_position(self):
        """测试坐标转换"""
        from app.services.pptx_generator import PptxGeneratorService
        from app.services.position_extractor import ElementPosition

        generator = PptxGeneratorService()

        element = ElementPosition(
            element_id="test",
            element_type="text",
            x=960,  # 中心 x
            y=540,  # 中心 y
            width=200,
            height=100,
        )

        left, top, width, height = generator._convert_position(element)

        # 验证转换后的值是 EMU 类型
        assert left is not None
        assert top is not None
        assert width is not None
        assert height is not None


class TestHtmlRenderer:
    """HTML 渲染服务测试 (需要 Playwright)"""

    def test_wrap_html_fragment(self):
        """测试包装 HTML 片段"""
        from app.services.html_renderer import HtmlRendererService

        service = HtmlRendererService()

        html_fragment = '<div data-pptx-slide><h1>标题</h1></div>'
        wrapped = service._wrap_html(html_fragment, 1920, 1080)

        assert "<!DOCTYPE html>" in wrapped
        assert "<html>" in wrapped
        assert "1920px" in wrapped
        assert "1080px" in wrapped
        assert html_fragment in wrapped

    def test_wrap_html_complete_document(self):
        """测试完整 HTML 文档不被重复包装"""
        from app.services.html_renderer import HtmlRendererService

        service = HtmlRendererService()

        complete_html = "<!DOCTYPE html><html><body>内容</body></html>"
        wrapped = service._wrap_html(complete_html, 1920, 1080)

        # 完整文档应该原样返回
        assert wrapped == complete_html


class TestRenderResult:
    """渲染结果测试"""

    def test_render_result_to_dict(self):
        """测试渲染结果转换为字典"""
        from app.services.html_renderer import RenderResult
        from app.services.position_extractor import ElementPosition

        result = RenderResult(
            screenshot=b"fake_image_data",
            elements=[
                ElementPosition(
                    element_id="test",
                    element_type="text",
                    x=0,
                    y=0,
                    width=100,
                    height=50,
                    content="测试",
                )
            ],
            metadata={"width": 1920, "height": 1080},
            width=1920,
            height=1080,
        )

        result_dict = result.to_dict()

        assert "screenshot_base64" in result_dict
        assert "elements" in result_dict
        assert len(result_dict["elements"]) == 1
        assert result_dict["width"] == 1920
        assert result_dict["height"] == 1080


class TestConfig:
    """配置测试"""

    def test_default_config(self):
        """测试默认配置"""
        from app.config import settings

        assert settings.APP_NAME == "PPTX Renderer Service"
        assert settings.PORT == 8006
        assert settings.DEFAULT_SLIDE_WIDTH == 1920
        assert settings.DEFAULT_SLIDE_HEIGHT == 1080

    def test_cors_origins_list(self):
        """测试 CORS 来源列表解析"""
        from app.config import settings

        origins = settings.cors_origins_list

        assert isinstance(origins, list)
        assert len(origins) > 0


# ============================================================
# 集成测试 (需要 Playwright 安装)
# ============================================================


@pytest.mark.asyncio
@pytest.mark.skipif(
    True,  # 默认跳过，需要 Playwright 时设为 False
    reason="需要安装 Playwright 浏览器"
)
class TestIntegration:
    """集成测试 (需要 Playwright)"""

    async def test_full_render_pipeline(self):
        """测试完整渲染流程"""
        from app.services.html_renderer import HtmlRendererService
        from app.services.pptx_generator import PptxGeneratorService

        renderer = HtmlRendererService()

        try:
            # 渲染 HTML
            result = await renderer.render_slide(SAMPLE_HTML)

            assert result.screenshot is not None
            assert len(result.screenshot) > 0
            assert len(result.elements) > 0

            # 生成 PPTX
            generator = PptxGeneratorService()
            pptx_bytes = generator.generate(
                elements=result.elements,
                screenshot=result.screenshot,
            )

            assert len(pptx_bytes) > 0
            assert pptx_bytes[:4] == b'PK\x03\x04'

        finally:
            await renderer.close()

    async def test_screenshot_only(self):
        """测试仅截图功能"""
        from app.services.html_renderer import HtmlRendererService

        renderer = HtmlRendererService()

        try:
            screenshot = await renderer.get_screenshot_only(MINIMAL_HTML)

            assert screenshot is not None
            assert len(screenshot) > 0
            # PNG 文件头
            assert screenshot[:8] == b'\x89PNG\r\n\x1a\n'

        finally:
            await renderer.close()


# ============================================================
# API 测试
# ============================================================


class TestAPI:
    """API 端点测试"""

    def test_request_models(self):
        """测试请求模型"""
        from app.api.v1.render import SlideRenderRequest, PreviewRequest

        # 测试 SlideRenderRequest
        request = SlideRenderRequest(
            html="<div>测试</div>",
            width=1920,
            height=1080,
        )
        assert request.html == "<div>测试</div>"
        assert request.width == 1920

        # 测试 PreviewRequest
        preview = PreviewRequest(
            html="<div>预览</div>",
            format="png",
            quality=95,
        )
        assert preview.format == "png"
        assert preview.quality == 95

    def test_response_models(self):
        """测试响应模型"""
        from app.api.v1.render import RenderResponse, ElementPositionResponse

        # 测试 ElementPositionResponse
        element = ElementPositionResponse(
            element_id="test",
            element_type="text",
            x=100,
            y=200,
            width=300,
            height=50,
        )
        assert element.element_id == "test"

        # 测试 RenderResponse
        response = RenderResponse(
            success=True,
            message="成功",
            elements_count=1,
            elements=[element],
        )
        assert response.success is True
        assert response.elements_count == 1
