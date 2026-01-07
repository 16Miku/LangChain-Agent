# ============================================================
# Presentation Service - Theme Service Tests
# 高级主题系统自动化测试
# ============================================================

import pytest
from typing import List

from app.services.theme_service import (
    ThemeType,
    ThemeColors,
    ThemeFonts,
    ThemeConfig,
    ThemeService,
    theme_service,
    THEME_CONFIGS,
)


class TestThemeType:
    """主题类型枚举测试"""

    def test_theme_type_count(self):
        """测试主题类型数量 (17种)"""
        theme_types = list(ThemeType)
        assert len(theme_types) == 17

    def test_theme_type_values(self):
        """测试主题类型值"""
        # 商务/专业
        assert ThemeType.MODERN_BUSINESS.value == "modern_business"
        assert ThemeType.CORPORATE_BLUE.value == "corporate_blue"
        assert ThemeType.ELEGANT_DARK.value == "elegant_dark"

        # 科技/创新
        assert ThemeType.DARK_TECH.value == "dark_tech"
        assert ThemeType.GRADIENT_PURPLE.value == "gradient_purple"
        assert ThemeType.NEON_FUTURE.value == "neon_future"

        # 简约/清新
        assert ThemeType.MINIMAL_WHITE.value == "minimal_white"
        assert ThemeType.NATURE_GREEN.value == "nature_green"
        assert ThemeType.SOFT_PASTEL.value == "soft_pastel"

        # 创意/活力
        assert ThemeType.CREATIVE_COLORFUL.value == "creative_colorful"
        assert ThemeType.WARM_SUNSET.value == "warm_sunset"

        # 学术/教育
        assert ThemeType.ACADEMIC_CLASSIC.value == "academic_classic"

        # 二次元/动漫
        assert ThemeType.ANIME_DARK.value == "anime_dark"
        assert ThemeType.ANIME_CUTE.value == "anime_cute"
        assert ThemeType.CYBERPUNK.value == "cyberpunk"
        assert ThemeType.EVA_NERV.value == "eva_nerv"
        assert ThemeType.RETRO_PIXEL.value == "retro_pixel"


class TestThemeColors:
    """主题颜色模型测试"""

    def test_theme_colors_creation(self):
        """测试主题颜色创建"""
        colors = ThemeColors(
            primary="#1e3a8a",
            secondary="#3b82f6",
            accent="#60a5fa",
            background="#ffffff",
            surface="#f8fafc",
            text_primary="#1e293b",
            text_secondary="#64748b",
            border="#e2e8f0",
        )

        assert colors.primary == "#1e3a8a"
        assert colors.background == "#ffffff"

    def test_theme_colors_defaults(self):
        """测试主题颜色默认值"""
        colors = ThemeColors(
            primary="#000000",
            secondary="#000000",
            accent="#000000",
            background="#ffffff",
            surface="#f0f0f0",
            text_primary="#000000",
            text_secondary="#666666",
            border="#cccccc",
        )

        assert colors.success == "#22c55e"
        assert colors.warning == "#f59e0b"
        assert colors.error == "#ef4444"


class TestThemeFonts:
    """主题字体模型测试"""

    def test_theme_fonts_creation(self):
        """测试主题字体创建"""
        fonts = ThemeFonts(
            title="Montserrat, sans-serif",
            subtitle="Open Sans, sans-serif",
            body="Open Sans, sans-serif",
        )

        assert "Montserrat" in fonts.title
        assert "Open Sans" in fonts.body

    def test_theme_fonts_default_code(self):
        """测试默认代码字体"""
        fonts = ThemeFonts(
            title="Arial",
            subtitle="Arial",
            body="Arial",
        )

        assert "Fira Code" in fonts.code
        assert "monospace" in fonts.code


class TestThemeConfigs:
    """主题配置字典测试"""

    def test_all_theme_types_have_configs(self):
        """测试所有主题类型都有配置"""
        for theme_type in ThemeType:
            assert theme_type.value in THEME_CONFIGS
            config = THEME_CONFIGS[theme_type.value]
            assert isinstance(config, ThemeConfig)

    def test_configs_count(self):
        """测试配置数量与枚举一致"""
        assert len(THEME_CONFIGS) == len(ThemeType)

    def test_modern_business_config(self):
        """测试现代商务主题配置"""
        config = THEME_CONFIGS["modern_business"]
        assert config.name == "现代商务"
        assert config.name_en == "Modern Business"
        assert "商业" in config.recommended_for[0] or "汇报" in config.recommended_for[0]

    def test_dark_tech_config(self):
        """测试科技深色主题配置"""
        config = THEME_CONFIGS["dark_tech"]
        assert config.name == "科技深色"
        assert "#00ff88" in config.colors.primary  # 霓虹绿
        assert "科技" in config.recommended_for[0]

    def test_all_configs_have_required_fields(self):
        """测试所有配置都有必需字段"""
        for theme_type, config in THEME_CONFIGS.items():
            assert config.name is not None
            assert config.name_en is not None
            assert config.description is not None
            assert config.colors is not None
            assert config.fonts is not None
            assert config.style is not None
            assert len(config.recommended_for) > 0
            assert config.preview_gradient is not None


class TestThemeService:
    """主题服务测试"""

    @pytest.fixture
    def service(self):
        """创建主题服务实例"""
        return ThemeService()

    def test_get_all_themes(self, service):
        """测试获取所有主题"""
        themes = service.get_all_themes()
        assert len(themes) == 17
        assert all(isinstance(config, ThemeConfig) for config in themes)

    def test_get_theme_valid(self, service):
        """测试获取有效主题"""
        config = service.get_theme("modern_business")
        assert config is not None
        assert config.name == "现代商务"

    def test_get_theme_invalid(self, service):
        """测试获取无效主题"""
        config = service.get_theme("non_existent_theme")
        assert config is None

    def test_get_theme_names(self, service):
        """测试获取主题名称映射"""
        names = service.get_theme_names()
        assert len(names) == 17
        assert names["modern_business"] == "现代商务"
        assert names["dark_tech"] == "科技深色"
        assert names["anime_dark"] == "二次元暗黑"
        assert names["eva_nerv"] == "EVA NERV"

    def test_validate_theme_valid(self, service):
        """测试验证有效主题"""
        assert service.validate_theme("modern_business") is True
        assert service.validate_theme("dark_tech") is True
        assert service.validate_theme("elegant_dark") is True

    def test_validate_theme_invalid(self, service):
        """测试验证无效主题"""
        assert service.validate_theme("invalid_theme") is False
        assert service.validate_theme("") is False

    def test_suggest_theme_business(self, service):
        """测试商务场景推荐"""
        assert service.suggest_theme("商务汇报") == "modern_business"
        assert service.suggest_theme("企业培训") == "corporate_blue"
        assert service.suggest_theme("正式会议") == "corporate_blue"

    def test_suggest_theme_tech(self, service):
        """测试科技场景推荐"""
        assert service.suggest_theme("科技产品发布") == "dark_tech"
        assert service.suggest_theme("AI人工智能") == "dark_tech"

    def test_suggest_theme_gaming(self, service):
        """测试游戏场景推荐"""
        assert service.suggest_theme("游戏发布") == "retro_pixel"
        assert service.suggest_theme("电竞比赛") == "neon_future"

    def test_suggest_theme_luxury(self, service):
        """测试高端场景推荐"""
        assert service.suggest_theme("高端品牌") == "elegant_dark"
        assert service.suggest_theme("奢华晚宴") == "elegant_dark"

    def test_suggest_theme_minimal(self, service):
        """测试简约场景推荐"""
        assert service.suggest_theme("简洁的报告") == "minimal_white"
        assert service.suggest_theme("简约风格") == "minimal_white"

    def test_suggest_theme_eco(self, service):
        """测试环保场景推荐"""
        assert service.suggest_theme("环保主题") == "nature_green"
        assert service.suggest_theme("健康生活") == "nature_green"

    def test_suggest_theme_creative(self, service):
        """测试创意场景推荐"""
        assert service.suggest_theme("创意提案") == "creative_colorful"
        assert service.suggest_theme("营销活动") == "creative_colorful"

    def test_suggest_theme_academic(self, service):
        """测试学术场景推荐"""
        assert service.suggest_theme("学术论文") == "academic_classic"
        assert service.suggest_theme("毕业论文答辩") == "academic_classic"
        assert service.suggest_theme("教育培训") == "academic_classic"

    def test_suggest_theme_fashion(self, service):
        """测试时尚场景推荐"""
        assert service.suggest_theme("时尚发布") == "gradient_purple"

    def test_suggest_theme_travel(self, service):
        """测试旅游美食场景推荐"""
        assert service.suggest_theme("旅游介绍") == "warm_sunset"
        assert service.suggest_theme("美食推荐") == "warm_sunset"

    def test_suggest_theme_default(self, service):
        """测试默认推荐"""
        assert service.suggest_theme("unknown_scenario") == "modern_business"
        assert service.suggest_theme("") == "modern_business"

    def test_get_themes_for_scenario(self, service):
        """测试获取场景相关主题"""
        themes = service.get_themes_for_scenario("商业汇报")
        assert len(themes) > 0
        # 商业相关主题应该在列表中
        assert any(t in ["modern_business", "corporate_blue"] for t in themes)

    def test_get_themes_for_scenario_no_match(self, service):
        """测试无匹配场景"""
        themes = service.get_themes_for_scenario("random_xyz_123")
        # 应该返回默认主题
        assert "modern_business" in themes

    def test_generate_theme_css(self, service):
        """测试生成主题 CSS"""
        css = service.generate_theme_css("modern_business")

        assert isinstance(css, str)
        assert len(css) > 0

        # 检查包含 CSS 变量
        assert "--color-primary" in css
        assert "--color-background" in css
        assert "--font-title" in css

    def test_generate_theme_css_invalid_fallback(self, service):
        """测试无效主题使用默认"""
        css = service.generate_theme_css("invalid_theme")

        # 应该返回默认主题的 CSS
        assert isinstance(css, str)
        assert "--color-primary" in css

    def test_generate_reveal_theme_css(self, service):
        """测试生成 Reveal.js 主题 CSS"""
        css = service.generate_reveal_theme_css("dark_tech")

        assert isinstance(css, str)
        assert len(css) > 0

        # 检查 Reveal.js 特定样式
        assert ".reveal" in css
        assert ".reveal h1" in css
        assert ".reveal h2" in css
        assert ".reveal code" in css

    def test_generate_reveal_theme_css_contains_colors(self, service):
        """测试 Reveal.js CSS 包含主题颜色"""
        css = service.generate_reveal_theme_css("dark_tech")
        config = THEME_CONFIGS["dark_tech"]

        # 检查颜色值
        assert config.colors.primary in css
        assert config.colors.background in css


class TestGlobalThemeService:
    """全局主题服务实例测试"""

    def test_global_instance_exists(self):
        """测试全局实例存在"""
        assert theme_service is not None
        assert isinstance(theme_service, ThemeService)

    def test_global_instance_works(self):
        """测试全局实例可用"""
        themes = theme_service.get_all_themes()
        assert len(themes) == 17

        config = theme_service.get_theme("modern_business")
        assert config is not None


class TestThemeConfigDetails:
    """主题配置详细测试"""

    def test_all_themes_have_chinese_names(self):
        """测试所有主题都有中文名称 (EVA NERV 除外)"""
        for theme_type, config in THEME_CONFIGS.items():
            # EVA NERV 是特殊主题，使用英文名称
            if theme_type == "eva_nerv":
                assert config.name == "EVA NERV"
            else:
                # 检查名称包含中文字符
                assert any('\u4e00' <= char <= '\u9fff' for char in config.name), f"{theme_type}: name should contain Chinese characters"

    def test_all_themes_have_english_names(self):
        """测试所有主题都有英文名称"""
        for theme_type, config in THEME_CONFIGS.items():
            # 检查英文名称只包含 ASCII 字符
            assert config.name_en.isascii() or ' ' in config.name_en

    def test_all_colors_are_valid_hex(self):
        """测试所有颜色都是有效的十六进制"""
        import re
        hex_pattern = re.compile(r'^#[0-9a-fA-F]{6}$')

        for theme_type, config in THEME_CONFIGS.items():
            colors = config.colors
            assert hex_pattern.match(colors.primary), f"{theme_type}: invalid primary color"
            assert hex_pattern.match(colors.secondary), f"{theme_type}: invalid secondary color"
            assert hex_pattern.match(colors.accent), f"{theme_type}: invalid accent color"
            assert hex_pattern.match(colors.background), f"{theme_type}: invalid background color"
            assert hex_pattern.match(colors.text_primary), f"{theme_type}: invalid text_primary color"

    def test_preview_gradients_are_valid(self):
        """测试预览渐变格式正确"""
        for theme_type, config in THEME_CONFIGS.items():
            assert config.preview_gradient.startswith("linear-gradient")
            assert "deg" in config.preview_gradient


class TestAnimeThemes:
    """二次元/动漫主题测试"""

    @pytest.fixture
    def service(self):
        """创建主题服务实例"""
        return ThemeService()

    def test_anime_dark_config(self):
        """测试二次元暗黑主题配置"""
        config = THEME_CONFIGS["anime_dark"]
        assert config.name == "二次元暗黑"
        assert config.name_en == "Anime Dark"
        assert "动漫" in config.recommended_for[0] or "游戏" in config.recommended_for[0]
        # 检查深色背景
        assert config.colors.background.startswith("#0")

    def test_anime_cute_config(self):
        """测试二次元可爱主题配置"""
        config = THEME_CONFIGS["anime_cute"]
        assert config.name == "二次元可爱"
        assert config.name_en == "Anime Cute"
        # 检查浅色背景
        assert config.colors.background.startswith("#fff")

    def test_cyberpunk_config(self):
        """测试赛博朋克主题配置"""
        config = THEME_CONFIGS["cyberpunk"]
        assert config.name == "赛博朋克"
        assert config.name_en == "Cyberpunk"
        # 检查深色背景
        assert config.colors.background.startswith("#1")

    def test_eva_nerv_config(self):
        """测试 EVA NERV 主题配置"""
        config = THEME_CONFIGS["eva_nerv"]
        assert config.name == "EVA NERV"
        assert config.name_en == "EVA NERV"
        # 检查经典 EVA 配色：紫、绿、橙
        assert "#5B2C6F" in config.colors.primary  # 初号机紫
        assert "#1ABC9C" in config.colors.secondary  # 初号机绿
        assert "#E74C3C" in config.colors.accent  # 贰号机橙红
        # 检查终端绿文字
        assert "#00FF00" in config.colors.text_primary

    def test_retro_pixel_config(self):
        """测试复古像素主题配置"""
        config = THEME_CONFIGS["retro_pixel"]
        assert config.name == "复古像素"
        assert config.name_en == "Retro Pixel"
        # 检查像素字体
        assert "Press Start 2P" in config.fonts.title

    def test_suggest_theme_anime(self, service):
        """测试动漫场景推荐"""
        assert service.suggest_theme("动漫介绍") == "anime_dark"
        assert service.suggest_theme("二次元活动") == "anime_dark"
        assert service.suggest_theme("番剧推荐") == "anime_dark"

    def test_suggest_theme_cute(self, service):
        """测试萌系场景推荐"""
        assert service.suggest_theme("萌系动漫") == "anime_cute"
        assert service.suggest_theme("可爱角色") == "anime_cute"

    def test_suggest_theme_cyberpunk(self, service):
        """测试赛博朋克场景推荐"""
        assert service.suggest_theme("赛博朋克世界") == "cyberpunk"
        assert service.suggest_theme("科幻机甲") == "cyberpunk"

    def test_suggest_theme_eva(self, service):
        """测试 EVA 场景推荐"""
        assert service.suggest_theme("eva介绍") == "eva_nerv"
        assert service.suggest_theme("新世纪福音战士") == "eva_nerv"
        assert service.suggest_theme("NERV组织") == "eva_nerv"

    def test_suggest_theme_pixel(self, service):
        """测试像素风场景推荐"""
        assert service.suggest_theme("像素艺术") == "retro_pixel"
        assert service.suggest_theme("复古游戏") == "retro_pixel"
