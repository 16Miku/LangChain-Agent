# ============================================================
# PPTX Export Service Tests
# PPTX 导出服务测试
# ============================================================

import pytest
import asyncio
import io
from zipfile import ZipFile

from app.services.pptx_export_service import PptxExportService, pptx_export_service


class TestPptxExportService:
    """PPTX 导出服务测试类"""

    @pytest.fixture
    def service(self):
        """创建服务实例"""
        return PptxExportService()

    @pytest.fixture
    def sample_presentation(self):
        """示例演示文稿数据"""
        return {
            "title": "测试演示文稿",
            "description": "这是一个测试演示文稿",
            "slides": [
                {
                    "title": "欢迎",
                    "content": "这是封面页的副标题",
                    "layout": "title_cover",
                    "notes": "封面页备注"
                },
                {
                    "title": "第一章",
                    "content": "",
                    "layout": "title_section",
                    "notes": ""
                },
                {
                    "title": "主要内容",
                    "content": "- 第一点内容\n- 第二点内容\n- 第三点内容",
                    "layout": "bullet_points",
                    "notes": "这是演讲者备注"
                },
                {
                    "title": "对比分析",
                    "content": "优点：\n- 简单易用\n- 性能优秀\n\n缺点：\n- 学习曲线\n- 文档不足",
                    "layout": "two_column",
                    "notes": ""
                },
                {
                    "title": "名人名言",
                    "content": "代码是写给人看的，顺便能在机器上运行。",
                    "layout": "quote_center",
                    "notes": ""
                },
                {
                    "title": "谢谢观看",
                    "content": "联系方式: test@example.com",
                    "layout": "thank_you",
                    "notes": ""
                }
            ],
            "theme": "modern_business"
        }

    # ============================================================
    # 基础功能测试
    # ============================================================

    def test_export_basic(self, service, sample_presentation):
        """测试基础导出功能"""
        result = asyncio.get_event_loop().run_until_complete(
            service.export_to_pptx(sample_presentation)
        )
        assert result is not None
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_export_valid_pptx(self, service, sample_presentation):
        """测试导出的文件是有效的 PPTX (ZIP 格式)"""
        result = asyncio.get_event_loop().run_until_complete(
            service.export_to_pptx(sample_presentation)
        )
        # PPTX 是 ZIP 格式
        with ZipFile(io.BytesIO(result), 'r') as zf:
            namelist = zf.namelist()
            assert '[Content_Types].xml' in namelist
            assert 'ppt/presentation.xml' in namelist

    def test_export_slide_count(self, service, sample_presentation):
        """测试导出的幻灯片数量正确"""
        result = asyncio.get_event_loop().run_until_complete(
            service.export_to_pptx(sample_presentation)
        )
        with ZipFile(io.BytesIO(result), 'r') as zf:
            slide_files = [n for n in zf.namelist() if n.startswith('ppt/slides/slide') and n.endswith('.xml')]
            assert len(slide_files) == len(sample_presentation["slides"])

    # ============================================================
    # 主题测试
    # ============================================================

    def test_export_with_different_themes(self, service, sample_presentation):
        """测试不同主题导出"""
        themes = ["modern_business", "dark_tech", "minimal_white", "anime_dark", "cyberpunk"]
        for theme in themes:
            result = asyncio.get_event_loop().run_until_complete(
                service.export_to_pptx(sample_presentation, theme=theme)
            )
            assert result is not None
            assert len(result) > 0

    def test_get_theme_colors(self, service):
        """测试获取主题配色"""
        colors = service._get_theme_colors("modern_business")
        assert "background" in colors
        assert "title" in colors
        assert "text" in colors
        assert "accent" in colors

    def test_get_theme_colors_fallback(self, service):
        """测试未知主题回退到默认"""
        colors = service._get_theme_colors("unknown_theme")
        default_colors = service._get_theme_colors("modern_business")
        assert colors == default_colors

    # ============================================================
    # 颜色转换测试
    # ============================================================

    def test_hex_to_rgb(self, service):
        """测试十六进制颜色转换"""
        rgb = service._hex_to_rgb("FF0000")
        # RGBColor 使用索引访问
        assert rgb[0] == 255  # red
        assert rgb[1] == 0    # green
        assert rgb[2] == 0    # blue

        rgb = service._hex_to_rgb("#00FF00")
        assert rgb[0] == 0
        assert rgb[1] == 255
        assert rgb[2] == 0

    # ============================================================
    # 内容解析测试
    # ============================================================

    def test_parse_content_bullets(self, service):
        """测试解析列表内容"""
        content = "- 第一项\n- 第二项\n- 第三项"
        lines = service._parse_content(content)
        assert len(lines) == 3
        assert lines[0][0] == "第一项"
        assert lines[0][2] is True  # is_bullet

    def test_parse_content_numbered(self, service):
        """测试解析编号列表"""
        content = "1. 第一步\n2. 第二步\n3. 第三步"
        lines = service._parse_content(content)
        assert len(lines) == 3
        assert lines[0][0] == "第一步"
        assert lines[0][2] is True

    def test_parse_content_mixed(self, service):
        """测试解析混合内容"""
        content = "标题文本\n- 列表项1\n- 列表项2"
        lines = service._parse_content(content)
        assert len(lines) == 3
        assert lines[0][2] is False  # 非列表项
        assert lines[1][2] is True   # 列表项

    def test_parse_content_with_newline_escape(self, service):
        """测试解析包含转义换行符的内容"""
        content = "第一行\\n第二行\\n第三行"
        lines = service._parse_content(content)
        assert len(lines) == 3

    # ============================================================
    # 布局测试
    # ============================================================

    def test_title_cover_layout(self, service):
        """测试封面页布局"""
        presentation = {"slides": [{"title": "标题", "content": "副标题", "layout": "title_cover"}]}
        result = asyncio.get_event_loop().run_until_complete(service.export_to_pptx(presentation))
        assert result is not None

    def test_section_layout(self, service):
        """测试章节页布局"""
        presentation = {"slides": [{"title": "第一章", "content": "", "layout": "title_section"}]}
        result = asyncio.get_event_loop().run_until_complete(service.export_to_pptx(presentation))
        assert result is not None

    def test_bullet_points_layout(self, service):
        """测试列表页布局"""
        presentation = {"slides": [{"title": "要点", "content": "- 点1\n- 点2", "layout": "bullet_points"}]}
        result = asyncio.get_event_loop().run_until_complete(service.export_to_pptx(presentation))
        assert result is not None

    def test_two_column_layout(self, service):
        """测试双栏布局"""
        presentation = {"slides": [{"title": "对比", "content": "左侧内容\n右侧内容", "layout": "two_column"}]}
        result = asyncio.get_event_loop().run_until_complete(service.export_to_pptx(presentation))
        assert result is not None

    def test_quote_layout(self, service):
        """测试引用页布局"""
        presentation = {"slides": [{"title": "作者", "content": "这是一段引用", "layout": "quote_center"}]}
        result = asyncio.get_event_loop().run_until_complete(service.export_to_pptx(presentation))
        assert result is not None

    def test_thank_you_layout(self, service):
        """测试感谢页布局"""
        presentation = {"slides": [{"title": "谢谢", "content": "联系方式", "layout": "thank_you"}]}
        result = asyncio.get_event_loop().run_until_complete(service.export_to_pptx(presentation))
        assert result is not None

    # ============================================================
    # 文件名生成测试
    # ============================================================

    def test_generate_filename(self, service):
        """测试文件名生成"""
        filename = service.generate_filename("测试演示文稿")
        assert filename.endswith(".pptx")
        assert "_" in filename

    def test_generate_filename_special_chars(self, service):
        """测试特殊字符文件名"""
        filename = service.generate_filename("Test / Presentation: 2024")
        assert filename.endswith(".pptx")
        assert "/" not in filename
        assert ":" not in filename

    # ============================================================
    # 边界情况测试
    # ============================================================

    def test_empty_slides(self, service):
        """测试空幻灯片列表"""
        presentation = {"slides": []}
        result = asyncio.get_event_loop().run_until_complete(service.export_to_pptx(presentation))
        assert result is not None

    def test_empty_content(self, service):
        """测试空内容幻灯片"""
        presentation = {"slides": [{"title": "标题", "content": "", "layout": "bullet_points"}]}
        result = asyncio.get_event_loop().run_until_complete(service.export_to_pptx(presentation))
        assert result is not None

    def test_long_content(self, service):
        """测试长内容"""
        long_content = "\n".join([f"- 这是第 {i} 个列表项" for i in range(20)])
        presentation = {"slides": [{"title": "长列表", "content": long_content, "layout": "bullet_points"}]}
        result = asyncio.get_event_loop().run_until_complete(service.export_to_pptx(presentation))
        assert result is not None

    def test_unicode_content(self, service):
        """测试 Unicode 内容"""
        presentation = {
            "slides": [{"title": "中文标题", "content": "日本語テスト\n한국어 테스트", "layout": "bullet_points"}]
        }
        result = asyncio.get_event_loop().run_until_complete(service.export_to_pptx(presentation))
        assert result is not None

    # ============================================================
    # 全局实例测试
    # ============================================================

    def test_global_instance(self, sample_presentation):
        """测试全局服务实例"""
        result = asyncio.get_event_loop().run_until_complete(
            pptx_export_service.export_to_pptx(sample_presentation)
        )
        assert result is not None
        assert len(result) > 0
