# ============================================================
# Presentation Service - Export Service Tests
# 导出服务自动化测试
# ============================================================

import pytest
from datetime import datetime

from app.services.export_service import (
    ExportService,
    export_service,
)


class TestExportService:
    """导出服务测试"""

    @pytest.fixture
    def service(self):
        """创建导出服务实例"""
        return ExportService()

    @pytest.fixture
    def sample_presentation(self):
        """示例演示文稿数据"""
        return {
            "id": "test-123",
            "title": "测试演示文稿",
            "description": "这是一个测试演示文稿",
            "theme": "modern_business",
            "target_audience": "general",
            "presentation_type": "informative",
            "slides": [
                {
                    "title": "封面",
                    "content": "这是封面页",
                    "layout": "title_cover",
                    "notes": "欢迎致辞",
                    "images": [],
                    "background": None,
                },
                {
                    "title": "列表页",
                    "content": "- 要点1\n- 要点2\n- 要点3",
                    "layout": "bullet_points",
                    "notes": None,
                    "images": [],
                    "background": None,
                },
                {
                    "title": "双栏布局",
                    "content": "左侧内容",
                    "layout": "two_column",
                    "notes": None,
                    "images": [
                        {
                            "url": "https://example.com/image.jpg",
                            "caption": "示例图片",
                            "alt": "示例",
                            "position": "right",
                            "size": "medium",
                        }
                    ],
                    "background": None,
                },
                {
                    "title": "感谢页",
                    "content": "谢谢观看！",
                    "layout": "thank_you",
                    "notes": None,
                    "images": [],
                    "background": None,
                },
            ],
        }

    def test_export_to_html_basic(self, service, sample_presentation):
        """测试基本 HTML 导出"""
        import asyncio

        html = asyncio.get_event_loop().run_until_complete(
            service.export_to_html(sample_presentation)
        )

        assert isinstance(html, str)
        assert len(html) > 0
        assert "<!DOCTYPE html>" in html
        assert "<html" in html
        assert "</html>" in html

    def test_export_html_contains_title(self, service, sample_presentation):
        """测试 HTML 包含标题"""
        import asyncio

        html = asyncio.get_event_loop().run_until_complete(
            service.export_to_html(sample_presentation)
        )

        assert "测试演示文稿" in html

    def test_export_html_contains_slides(self, service, sample_presentation):
        """测试 HTML 包含幻灯片"""
        import asyncio

        html = asyncio.get_event_loop().run_until_complete(
            service.export_to_html(sample_presentation)
        )

        assert "<section" in html
        assert "</section>" in html
        # 应该有 4 个 section (4 张幻灯片)
        assert html.count("<section") >= 4

    def test_export_html_contains_reveal_js(self, service, sample_presentation):
        """测试 HTML 包含 Reveal.js CDN"""
        import asyncio

        html = asyncio.get_event_loop().run_until_complete(
            service.export_to_html(
                sample_presentation,
                include_reveal_js=True
            )
        )

        assert "reveal.js" in html
        assert "reveal.min.css" in html
        assert "reveal.min.js" in html

    def test_export_html_without_reveal_js(self, service, sample_presentation):
        """测试不包含 Reveal.js 的导出"""
        import asyncio

        html = asyncio.get_event_loop().run_until_complete(
            service.export_to_html(
                sample_presentation,
                include_reveal_js=False
            )
        )

        # 不应该有 Reveal.js 的脚本和样式链接
        assert "reveal.min.js" not in html
        assert "reveal.min.css" not in html
        # 注意：lang="zh-CN" 中包含 "cdn"，所以不能简单检查 "cdn" 关键字

    def test_export_html_with_theme_css(self, service, sample_presentation):
        """测试 HTML 包含主题 CSS"""
        import asyncio

        theme_css = """
        :root {
            --color-primary: #1e3a8a;
            --color-background: #ffffff;
        }
        """

        html = asyncio.get_event_loop().run_until_complete(
            service.export_to_html(
                sample_presentation,
                theme_css=theme_css
            )
        )

        assert "--color-primary: #1e3a8a" in html
        assert "--color-background: #ffffff" in html

    def test_escape_html(self, service):
        """测试 HTML 转义"""
        assert service._escape_html("<script>") == "&lt;script&gt;"
        assert service._escape_html("a & b") == "a &amp; b"
        assert service._escape_html('"quoted"') == "&quot;quoted&quot;"
        assert service._escape_html("'single'") == "&#39;single&#39;"

    def test_escape_html_empty(self, service):
        """测试空字符串转义"""
        assert service._escape_html("") == ""
        assert service._escape_html(None) == ""

    def test_markdown_to_html_basic(self, service):
        """测试基本 Markdown 转 HTML"""
        html = service._markdown_to_html("这是普通文本")
        assert "<p>这是普通文本</p>" in html

    def test_markdown_to_html_list(self, service):
        """测试列表 Markdown 转 HTML"""
        html = service._markdown_to_html("- 项目1\n- 项目2\n- 项目3")
        assert "<ul>" in html  # 确保有开始标签
        assert "<li>项目1</li>" in html
        assert "<li>项目2</li>" in html
        assert "<li>项目3</li>" in html
        assert "</ul>" in html

    def test_markdown_to_html_list_with_literal_newline(self, service):
        """测试字面量换行符 \\n 的处理"""
        # 模拟从数据库读取的字面量 \n
        html = service._markdown_to_html("- 项目1\\n- 项目2\\n- 项目3")
        assert "<ul>" in html
        assert "<li>项目1</li>" in html
        assert "<li>项目2</li>" in html
        assert "<li>项目3</li>" in html
        assert "</ul>" in html

    def test_markdown_to_html_headings(self, service):
        """测试标题 Markdown 转 HTML"""
        html = service._markdown_to_html("# 标题1\n## 标题2\n### 标题3")
        assert "<h1>标题1</h1>" in html
        assert "<h2>标题2</h2>" in html
        assert "<h3>标题3</h3>" in html

    def test_markdown_to_html_empty(self, service):
        """测试空 Markdown"""
        html = service._markdown_to_html("")
        assert html == ""

    def test_generate_slides_html(self, service, sample_presentation):
        """测试生成幻灯片 HTML"""
        html = service._generate_slides_html(sample_presentation["slides"])
        assert isinstance(html, str)
        assert len(html) > 0
        assert "<section" in html

    def test_generate_slide_html_title_cover(self, service):
        """测试封面页 HTML 生成"""
        slide = {
            "title": "封面标题",
            "content": "封面内容",
            "layout": "title_cover",
            "notes": None,
            "images": [],
            "background": "#ffffff",
        }

        html = service._generate_slide_html(slide, 0)
        assert "<h1>封面标题</h1>" in html  # 封面页使用 h1
        assert "title-cover" in html
        assert "background-color: #ffffff" in html

    def test_generate_slide_html_with_background_image(self, service):
        """测试带背景图片的幻灯片"""
        slide = {
            "title": "测试",
            "content": "内容",
            "layout": "bullet_points",
            "notes": None,
            "images": [],
            "background": "https://example.com/bg.jpg",
        }

        html = service._generate_slide_html(slide, 0)
        assert "background-image" in html
        assert "https://example.com/bg.jpg" in html

    def test_generate_slide_html_with_notes(self, service):
        """测试带备注的幻灯片"""
        slide = {
            "title": "测试",
            "content": "内容",
            "layout": "bullet_points",
            "notes": "这是演讲者备注",
            "images": [],
            "background": None,
        }

        html = service._generate_slide_html(slide, 0)
        assert "<aside class=\"notes\">" in html
        assert "这是演讲者备注" in html

    def test_generate_images_html(self, service):
        """测试图片 HTML 生成"""
        images = [
            {
                "url": "https://example.com/img1.jpg",
                "caption": "图片1",
                "alt": "alt1",
                "position": "left",
                "size": "medium",
            },
            {
                "url": "https://example.com/img2.jpg",
                "caption": None,
                "alt": "alt2",
                "position": "right",
                "size": "large",
            },
        ]

        html = service._generate_images_html(images)
        assert "https://example.com/img1.jpg" in html
        assert "https://example.com/img2.jpg" in html
        assert "图片1" in html
        assert "alt1" in html
        assert "alt2" in html

    def test_generate_images_html_base64(self, service):
        """测试 Base64 图片 HTML 生成"""
        images = [
            {
                "url": "data:image/png;base64,iVBORw0KGgoAAAANS",
                "caption": None,
                "alt": "base64img",
                "position": "left",
                "size": "medium",
            },
        ]

        html = service._generate_images_html(images)
        assert "data:image/png;base64,iVBORw0KGgoAAAANS" in html
        assert "base64img" in html

    def test_generate_images_html_empty(self, service):
        """测试空图片列表"""
        html = service._generate_images_html([])
        assert html == ""

    def test_generate_filename(self, service):
        """测试文件名生成"""
        filename = service.generate_filename("我的演示文稿", "html")
        assert filename.endswith(".html")
        assert "my" in filename.lower() or "演示文稿" in filename

    def test_generate_filename_sanitization(self, service):
        """测试文件名清理"""
        filename = service.generate_filename("Test <Title> & More", "html")
        # 特殊字符应该被清理
        assert "<" not in filename
        assert ">" not in filename
        assert "&" not in filename

    def test_generate_metric_cards(self, service):
        """测试指标卡片生成"""
        content = """用户数: 1000
收入: 500万
增长率: 25%"""

        html = service._generate_metric_cards(content)
        assert "metric-grid" in html
        assert "1000" in html
        assert "500万" in html
        assert "25%" in html
        assert "用户数" in html
        assert "收入" in html
        assert "增长率" in html

    def test_generate_timeline(self, service):
        """测试时间线生成"""
        content = """2020: 项目启动
2021: 产品发布
2022: 用户突破百万"""

        html = service._generate_timeline(content)
        assert "timeline" in html
        assert "timeline-item" in html

    def test_generate_flow_steps(self, service):
        """测试流程步骤生成"""
        content = """1. 需求分析
2. 设计
3. 开发
4. 测试"""

        html = service._generate_flow_steps(content)
        assert "flow-step" in html

    def test_split_content_for_columns(self, service):
        """测试内容分割"""
        content = """第一部分内容

第二部分内容

第三部分内容"""

        columns = service._split_content_for_columns(content, 3)
        assert len(columns) == 3

    def test_generate_content_by_layout_two_column(self, service):
        """测试双栏布局内容生成"""
        slide = {
            "title": "双栏测试",
            "content": "左侧内容",
            "layout": "two_column",
            "notes": None,
            "images": [],
            "background": None,
        }

        html = service._generate_content_by_layout(
            "two_column",
            "左侧内容",
            [],
            slide
        )
        assert "two-column" in html

    def test_generate_content_by_layout_blank(self, service):
        """测试空白布局"""
        slide = {
            "title": "空白页",
            "content": "",
            "layout": "blank",
            "notes": None,
            "images": [],
            "background": None,
        }

        html = service._generate_content_by_layout(
            "blank",
            "",
            [],
            slide
        )
        # 空白布局应该没有内容
        assert html.strip() == ""

    def test_generate_content_by_layout_quote_center(self, service):
        """测试引用布局"""
        slide = {
            "title": "引用",
            "content": "这是一句名言",
            "layout": "quote_center",
            "notes": None,
            "images": [],
            "background": None,
        }

        html = service._generate_content_by_layout(
            "quote_center",
            "这是一句名言",
            [],
            slide
        )
        assert "quote-block" in html
        assert "这是一句名言" in html


class TestGlobalExportService:
    """全局导出服务实例测试"""

    def test_global_instance_exists(self):
        """测试全局实例存在"""
        assert export_service is not None
        assert isinstance(export_service, ExportService)

    def test_global_instance_methods(self):
        """测试全局实例方法可用"""
        # 测试转义方法
        result = export_service._escape_html("<test>")
        assert result == "&lt;test&gt;"

        # 测试文件名生成
        filename = export_service.generate_filename("测试", "html")
        assert filename.endswith(".html")


class TestExportServiceEdgeCases:
    """导出服务边界情况测试"""

    @pytest.fixture
    def service(self):
        return ExportService()

    def test_export_empty_slides(self, service):
        """测试空幻灯片导出"""
        import asyncio

        presentation = {
            "id": "test",
            "title": "空演示",
            "description": "",
            "theme": "modern_business",
            "target_audience": "general",
            "presentation_type": "informative",
            "slides": [],
        }

        html = asyncio.get_event_loop().run_until_complete(
            service.export_to_html(presentation)
        )

        assert "<!DOCTYPE html>" in html
        assert "空演示" in html

    def test_export_slide_with_empty_fields(self, service):
        """测试字段为空的幻灯片"""
        slide = {
            "title": "",
            "content": "",
            "layout": "bullet_points",
            "notes": "",
            "images": [],
            "background": None,
        }

        html = service._generate_slide_html(slide, 0)
        assert "<section" in html
        assert "</section>" in html

    def test_export_with_special_characters(self, service):
        """测试特殊字符处理"""
        assert "&lt;" in service._escape_html("<")
        assert "&gt;" in service._escape_html(">")
        assert "&amp;" in service._escape_html("&")
        assert "&quot;" in service._escape_html('"')

    def test_markdown_with_mixed_content(self, service):
        """测试混合 Markdown 内容"""
        content = """# 标题

普通段落

- 列表1
- 列表2

**粗体文本**"""

        html = service._markdown_to_html(content)
        assert "<h1>标题</h1>" in html
        assert "<li>列表1</li>" in html
        assert "<strong>" in html
