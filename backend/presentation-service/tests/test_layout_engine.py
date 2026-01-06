# ============================================================
# Presentation Service - Layout Engine Tests
# 智能布局引擎自动化测试
# ============================================================

import pytest
from typing import List

from app.services.layout_engine import (
    LayoutType,
    LayoutConfig,
    LayoutEngine,
    layout_engine,
    LAYOUT_CONFIGS,
)


class TestLayoutType:
    """布局类型枚举测试"""

    def test_layout_type_count(self):
        """测试布局类型数量 (19种)"""
        layout_types = list(LayoutType)
        assert len(layout_types) == 19

    def test_layout_type_values(self):
        """测试布局类型值"""
        # 基础布局
        assert LayoutType.TITLE_COVER.value == "title_cover"
        assert LayoutType.TITLE_SECTION.value == "title_section"
        assert LayoutType.BULLET_POINTS.value == "bullet_points"
        assert LayoutType.TWO_COLUMN.value == "two_column"
        assert LayoutType.IMAGE_TEXT.value == "image_text"

        # 数据展示
        assert LayoutType.CHART_SINGLE.value == "chart_single"
        assert LayoutType.CHART_DUAL.value == "chart_dual"
        assert LayoutType.DATA_TABLE.value == "data_table"
        assert LayoutType.METRIC_CARD.value == "metric_card"

        # 特殊效果
        assert LayoutType.QUOTE_CENTER.value == "quote_center"
        assert LayoutType.TIMELINE.value == "timeline"
        assert LayoutType.PROCESS_FLOW.value == "process_flow"
        assert LayoutType.COMPARISON.value == "comparison"
        assert LayoutType.GALLERY.value == "gallery"

        # 结尾
        assert LayoutType.THANK_YOU.value == "thank_you"
        assert LayoutType.CONTACT.value == "contact"

        # 新增
        assert LayoutType.BLANK.value == "blank"
        assert LayoutType.IMAGE_FULL.value == "image_full"
        assert LayoutType.THREE_COLUMN.value == "three_column"


class TestLayoutConfig:
    """布局配置模型测试"""

    def test_layout_config_creation(self):
        """测试布局配置创建"""
        config = LayoutConfig(
            type=LayoutType.BULLET_POINTS,
            name="列表页",
            description="标题 + 3-6 个要点列表",
            css_class="layout-bullet-points",
            supports_images=True,
            supports_charts=False,
            max_content_length=500,
            recommended_for=["content", "points"],
        )

        assert config.type == LayoutType.BULLET_POINTS
        assert config.name == "列表页"
        assert config.supports_images is True
        assert config.supports_charts is False
        assert "content" in config.recommended_for

    def test_layout_config_defaults(self):
        """测试布局配置默认值"""
        config = LayoutConfig(
            type=LayoutType.BLANK,
            name="空白页",
            description="自由布局",
            css_class="layout-blank",
        )

        assert config.supports_images is True  # 默认 True
        assert config.supports_charts is False  # 默认 False
        assert config.max_content_length == 500  # 默认 500
        assert config.recommended_for == []  # 默认空列表


class TestLayoutConfigs:
    """布局配置字典测试"""

    def test_all_layout_types_have_configs(self):
        """测试所有布局类型都有配置"""
        for layout_type in LayoutType:
            assert layout_type.value in LAYOUT_CONFIGS
            config = LAYOUT_CONFIGS[layout_type.value]
            assert isinstance(config, LayoutConfig)

    def test_configs_count(self):
        """测试配置数量与枚举一致"""
        assert len(LAYOUT_CONFIGS) == len(LayoutType)

    def test_title_cover_config(self):
        """测试封面页配置"""
        config = LAYOUT_CONFIGS["title_cover"]
        assert config.name == "封面页"
        assert config.css_class == "layout-title-cover"
        assert "opening" in config.recommended_for
        assert "intro" in config.recommended_for

    def test_chart_layouts_support_charts(self):
        """测试图表布局支持图表"""
        assert LAYOUT_CONFIGS["chart_single"].supports_charts is True
        assert LAYOUT_CONFIGS["chart_dual"].supports_charts is True

    def test_text_only_layouts(self):
        """测试纯文本布局不支持图片"""
        assert LAYOUT_CONFIGS["title_section"].supports_images is False
        assert LAYOUT_CONFIGS["quote_center"].supports_images is False
        assert LAYOUT_CONFIGS["thank_you"].supports_images is False


class TestLayoutEngine:
    """布局引擎测试"""

    @pytest.fixture
    def engine(self):
        """创建布局引擎实例"""
        return LayoutEngine()

    def test_get_all_layouts(self, engine):
        """测试获取所有布局"""
        layouts = engine.get_all_layouts()
        assert len(layouts) == 19
        assert all(isinstance(config, LayoutConfig) for config in layouts)

    def test_get_layout_valid(self, engine):
        """测试获取有效布局"""
        config = engine.get_layout("bullet_points")
        assert config is not None
        assert config.name == "列表页"

    def test_get_layout_invalid(self, engine):
        """测试获取无效布局"""
        config = engine.get_layout("non_existent_layout")
        assert config is None

    def test_get_layout_names(self, engine):
        """测试获取布局名称映射"""
        names = engine.get_layout_names()
        assert len(names) == 19
        assert names["title_cover"] == "封面页"
        assert names["bullet_points"] == "列表页"
        assert names["thank_you"] == "结尾页"

    def test_suggest_layout_opening(self, engine):
        """测试推荐开场布局"""
        assert engine.suggest_layout("opening") == "title_cover"
        assert engine.suggest_layout("intro") == "title_cover"

    def test_suggest_layout_section(self, engine):
        """测试推荐章节布局"""
        assert engine.suggest_layout("section") == "title_section"
        assert engine.suggest_layout("chapter") == "title_section"

    def test_suggest_layout_content(self, engine):
        """测试推荐内容布局"""
        assert engine.suggest_layout("content") == "bullet_points"
        assert engine.suggest_layout("points") == "bullet_points"
        assert engine.suggest_layout("features") == "bullet_points"

    def test_suggest_layout_data(self, engine):
        """测试推荐数据布局"""
        assert engine.suggest_layout("chart") == "chart_single"
        assert engine.suggest_layout("data") == "chart_single"
        assert engine.suggest_layout("statistics") == "chart_single"

    def test_suggest_layout_timeline(self, engine):
        """测试推荐时间线布局"""
        assert engine.suggest_layout("timeline") == "timeline"
        assert engine.suggest_layout("history") == "timeline"
        assert engine.suggest_layout("evolution") == "timeline"

    def test_suggest_layout_process(self, engine):
        """测试推荐流程布局"""
        assert engine.suggest_layout("process") == "process_flow"
        assert engine.suggest_layout("workflow") == "process_flow"
        assert engine.suggest_layout("steps") == "process_flow"

    def test_suggest_layout_comparison(self, engine):
        """测试推荐对比布局"""
        assert engine.suggest_layout("vs") == "comparison"
        # "comparison" 可能匹配 two_column 或 comparison (都有这个关键词)
        # 只检查是否在对比相关布局中
        assert engine.suggest_layout("comparison") in ["comparison", "two_column"]
        assert engine.suggest_layout("pros-cons") == "comparison"

    def test_suggest_layout_ending(self, engine):
        """测试推荐结尾布局"""
        assert engine.suggest_layout("ending") == "thank_you"
        assert engine.suggest_layout("thanks") == "thank_you"
        assert engine.suggest_layout("qa") == "thank_you"

    def test_suggest_layout_contact(self, engine):
        """测试推荐联系方式布局"""
        assert engine.suggest_layout("contact") == "contact"
        assert engine.suggest_layout("social") == "contact"
        assert engine.suggest_layout("info") == "contact"

    def test_suggest_layout_default(self, engine):
        """测试默认推荐"""
        assert engine.suggest_layout("unknown_type") == "bullet_points"
        assert engine.suggest_layout("") == "bullet_points"

    def test_suggest_layouts_for_presentation_basic(self, engine):
        """测试演示文稿布局推荐 (基础)"""
        layouts = engine.suggest_layouts_for_presentation(slide_count=5)

        assert len(layouts) == 5
        assert layouts[0] == "title_cover"  # 封面
        assert layouts[-1] == "thank_you"  # 结尾

    def test_suggest_layouts_for_presentation_with_section(self, engine):
        """测试演示文稿布局推荐 (带章节页)"""
        layouts = engine.suggest_layouts_for_presentation(slide_count=6)

        assert len(layouts) == 6
        assert layouts[0] == "title_cover"
        assert layouts[1] == "title_section"  # 章节页
        assert layouts[-1] == "thank_you"

    def test_suggest_layouts_for_presentation_with_data(self, engine):
        """测试演示文稿布局推荐 (带数据图表)"""
        layouts = engine.suggest_layouts_for_presentation(
            slide_count=6, has_data=True
        )

        assert len(layouts) == 6
        # 应该包含图表布局
        assert any(
            layout in ["chart_single", "metric_card"] for layout in layouts
        )

    def test_suggest_layouts_for_presentation_with_timeline(self, engine):
        """测试演示文稿布局推荐 (带时间线)"""
        layouts = engine.suggest_layouts_for_presentation(
            slide_count=6, has_timeline=True
        )

        assert len(layouts) == 6
        assert "timeline" in layouts

    def test_suggest_layouts_for_presentation_with_comparison(self, engine):
        """测试演示文稿布局推荐 (带对比)"""
        layouts = engine.suggest_layouts_for_presentation(
            slide_count=6, has_comparison=True
        )

        assert len(layouts) == 6
        # 应该包含对比布局
        assert any(
            layout in ["comparison", "two_column"] for layout in layouts
        )

    def test_generate_layout_css(self, engine):
        """测试生成布局 CSS"""
        css = engine.generate_layout_css()

        assert isinstance(css, str)
        assert len(css) > 0

        # 检查包含所有布局的 CSS 类
        assert ".layout-title-cover" in css
        assert ".layout-bullet-points" in css
        assert ".layout-timeline" in css
        assert ".layout-metric-card" in css
        assert ".layout-thank-you" in css

    def test_generate_layout_css_with_theme(self, engine):
        """测试带主题的布局 CSS"""
        css = engine.generate_layout_css(theme="dark_tech")

        assert isinstance(css, str)
        assert "dark_tech" in css

    def test_get_layout_html_template_valid(self, engine):
        """测试获取有效布局模板"""
        template = engine.get_layout_html_template("title_cover")

        assert isinstance(template, str)
        assert "layout-title-cover" in template
        assert "{title}" in template

    def test_get_layout_html_template_bullet_points(self, engine):
        """测试获取列表页模板"""
        template = engine.get_layout_html_template("bullet_points")

        assert "layout-bullet-points" in template
        assert "{title}" in template
        assert "{content}" in template

    def test_get_layout_html_template_two_column(self, engine):
        """测试获取双栏布局模板"""
        template = engine.get_layout_html_template("two_column")

        assert "layout-two-column" in template
        assert "{left_title}" in template
        assert "{right_title}" in template

    def test_get_layout_html_template_timeline(self, engine):
        """测试获取时间线模板"""
        template = engine.get_layout_html_template("timeline")

        assert "layout-timeline" in template
        assert "{events}" in template

    def test_get_layout_html_template_invalid(self, engine):
        """测试获取无效布局模板 (返回默认)"""
        template = engine.get_layout_html_template("invalid_layout")

        # 应该返回默认的 bullet_points 模板
        assert "layout-bullet-points" in template

    def test_validate_layout_valid(self, engine):
        """测试验证有效布局"""
        assert engine.validate_layout("title_cover") is True
        assert engine.validate_layout("bullet_points") is True
        assert engine.validate_layout("timeline") is True

    def test_validate_layout_invalid(self, engine):
        """测试验证无效布局"""
        assert engine.validate_layout("invalid_layout") is False
        assert engine.validate_layout("") is False
        assert engine.validate_layout("non_existent") is False

    def test_get_compatible_layouts_short_content(self, engine):
        """测试短内容兼容布局"""
        compatible = engine.get_compatible_layouts(content_length=100)

        assert len(compatible) > 0
        # 短内容应该兼容所有布局
        assert "title_cover" in compatible
        assert "bullet_points" in compatible

    def test_get_compatible_layouts_long_content(self, engine):
        """测试长内容兼容布局"""
        compatible = engine.get_compatible_layouts(content_length=600)

        assert len(compatible) > 0
        # 长内容应该排除一些布局
        assert "title_cover" not in compatible  # max 200
        assert "blank" in compatible  # max 800

    def test_get_compatible_layouts_with_images(self, engine):
        """测试带图片的兼容布局"""
        compatible = engine.get_compatible_layouts(
            content_length=100, has_images=True
        )

        # 应该排除不支持图片的布局
        assert "title_section" not in compatible
        assert "quote_center" not in compatible

        # 应该包含支持图片的布局
        assert "bullet_points" in compatible
        assert "image_text" in compatible


class TestGlobalLayoutEngine:
    """全局布局引擎实例测试"""

    def test_global_instance_exists(self):
        """测试全局实例存在"""
        assert layout_engine is not None
        assert isinstance(layout_engine, LayoutEngine)

    def test_global_instance_works(self):
        """测试全局实例可用"""
        layouts = layout_engine.get_all_layouts()
        assert len(layouts) == 19

        config = layout_engine.get_layout("bullet_points")
        assert config is not None
