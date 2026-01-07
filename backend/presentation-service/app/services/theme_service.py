# ============================================================
# Presentation Service - Theme Service
# 高级主题系统 - 支持 10+ 精品主题
# ============================================================

from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel
from functools import lru_cache


class ThemeType(str, Enum):
    """主题类型枚举"""

    # === 商务/专业 ===
    MODERN_BUSINESS = "modern_business"  # 现代商务 - 蓝色系，专业简洁
    CORPORATE_BLUE = "corporate_blue"  # 企业蓝 - 深蓝色，正式稳重
    ELEGANT_DARK = "elegant_dark"  # 典雅深色 - 深灰金色，高端奢华

    # === 科技/创新 ===
    DARK_TECH = "dark_tech"  # 科技深色 - 黑色霓虹，科技感强
    GRADIENT_PURPLE = "gradient_purple"  # 渐变紫 - 紫色渐变，现代时尚
    NEON_FUTURE = "neon_future"  # 霓虹未来 - 赛博朋克风格

    # === 简约/清新 ===
    MINIMAL_WHITE = "minimal_white"  # 极简白 - 纯净简洁
    NATURE_GREEN = "nature_green"  # 自然绿 - 环保清新
    SOFT_PASTEL = "soft_pastel"  # 柔和粉彩 - 温馨柔美

    # === 创意/活力 ===
    CREATIVE_COLORFUL = "creative_colorful"  # 创意多彩 - 活泼鲜艳
    WARM_SUNSET = "warm_sunset"  # 暖阳落日 - 温暖橙红

    # === 学术/教育 ===
    ACADEMIC_CLASSIC = "academic_classic"  # 学术经典 - 传统正式

    # === 二次元/动漫 ===
    ANIME_DARK = "anime_dark"  # 二次元暗黑 - 深色背景 + 霓虹色
    ANIME_CUTE = "anime_cute"  # 二次元可爱 - 粉彩色系，萌系风格
    CYBERPUNK = "cyberpunk"  # 赛博朋克 - 紫/青/粉，科幻机甲
    EVA_NERV = "eva_nerv"  # EVA NERV - 新世纪福音战士专用
    RETRO_PIXEL = "retro_pixel"  # 复古像素 - 8-bit 游戏风格


class ThemeColors(BaseModel):
    """主题颜色配置"""
    primary: str  # 主色
    secondary: str  # 次要色
    accent: str  # 强调色
    background: str  # 背景色
    surface: str  # 表面色 (卡片等)
    text_primary: str  # 主文本色
    text_secondary: str  # 次要文本色
    border: str  # 边框色
    success: str = "#22c55e"  # 成功色
    warning: str = "#f59e0b"  # 警告色
    error: str = "#ef4444"  # 错误色


class ThemeFonts(BaseModel):
    """主题字体配置"""
    title: str  # 标题字体
    subtitle: str  # 副标题字体
    body: str  # 正文字体
    code: str = "Fira Code, Monaco, Consolas, monospace"  # 代码字体


class ThemeConfig(BaseModel):
    """完整主题配置"""
    type: ThemeType
    name: str
    name_en: str
    description: str
    colors: ThemeColors
    fonts: ThemeFonts
    style: str  # 风格描述
    recommended_for: List[str]  # 推荐使用场景
    preview_gradient: str  # 预览渐变色


# ============================================================
# 主题配置定义
# ============================================================

THEME_CONFIGS: Dict[str, ThemeConfig] = {
    # === 现代商务 ===
    ThemeType.MODERN_BUSINESS.value: ThemeConfig(
        type=ThemeType.MODERN_BUSINESS,
        name="现代商务",
        name_en="Modern Business",
        description="专业简洁的蓝色商务风格，适合企业汇报和商业演示",
        colors=ThemeColors(
            primary="#1e3a8a",
            secondary="#3b82f6",
            accent="#60a5fa",
            background="#ffffff",
            surface="#f8fafc",
            text_primary="#1e293b",
            text_secondary="#64748b",
            border="#e2e8f0",
        ),
        fonts=ThemeFonts(
            title="Montserrat, 'Noto Sans SC', sans-serif",
            subtitle="Open Sans, 'Noto Sans SC', sans-serif",
            body="Open Sans, 'Noto Sans SC', sans-serif",
        ),
        style="clean, professional, gradient accents",
        recommended_for=["商业汇报", "工作总结", "项目提案", "数据分析"],
        preview_gradient="linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%)",
    ),

    # === 企业蓝 ===
    ThemeType.CORPORATE_BLUE.value: ThemeConfig(
        type=ThemeType.CORPORATE_BLUE,
        name="企业蓝",
        name_en="Corporate Blue",
        description="深蓝色正式风格，适合大型企业和正式场合",
        colors=ThemeColors(
            primary="#0c4a6e",
            secondary="#0369a1",
            accent="#38bdf8",
            background="#f0f9ff",
            surface="#ffffff",
            text_primary="#0c4a6e",
            text_secondary="#475569",
            border="#bae6fd",
        ),
        fonts=ThemeFonts(
            title="Roboto, 'Noto Sans SC', sans-serif",
            subtitle="Roboto, 'Noto Sans SC', sans-serif",
            body="Roboto, 'Noto Sans SC', sans-serif",
        ),
        style="formal, trustworthy, corporate",
        recommended_for=["年度报告", "投资者会议", "正式汇报", "企业培训"],
        preview_gradient="linear-gradient(135deg, #0c4a6e 0%, #0369a1 100%)",
    ),

    # === 典雅深色 ===
    ThemeType.ELEGANT_DARK.value: ThemeConfig(
        type=ThemeType.ELEGANT_DARK,
        name="典雅深色",
        name_en="Elegant Dark",
        description="深色背景配金色点缀，高端奢华感",
        colors=ThemeColors(
            primary="#d4af37",
            secondary="#f4e4bc",
            accent="#ffd700",
            background="#1a1a1a",
            surface="#2d2d2d",
            text_primary="#f4f4f4",
            text_secondary="#a3a3a3",
            border="#404040",
        ),
        fonts=ThemeFonts(
            title="Playfair Display, 'Noto Serif SC', serif",
            subtitle="Lora, 'Noto Serif SC', serif",
            body="Lora, 'Noto Serif SC', serif",
        ),
        style="luxury, gold accents, elegant",
        recommended_for=["高端品牌", "奢侈品", "颁奖典礼", "VIP活动"],
        preview_gradient="linear-gradient(135deg, #1a1a1a 0%, #d4af37 100%)",
    ),

    # === 科技深色 ===
    ThemeType.DARK_TECH.value: ThemeConfig(
        type=ThemeType.DARK_TECH,
        name="科技深色",
        name_en="Dark Tech",
        description="黑色背景配霓虹色，强烈科技感",
        colors=ThemeColors(
            primary="#00ff88",
            secondary="#00d4ff",
            accent="#ff00ff",
            background="#0a0a0a",
            surface="#1a1a2e",
            text_primary="#e0e0e0",
            text_secondary="#888888",
            border="#2a2a4a",
        ),
        fonts=ThemeFonts(
            title="Rajdhani, 'Noto Sans SC', sans-serif",
            subtitle="Roboto Mono, 'Noto Sans SC', sans-serif",
            body="Roboto, 'Noto Sans SC', sans-serif",
        ),
        style="cyberpunk, neon, futuristic",
        recommended_for=["科技产品", "AI/ML", "游戏", "创新发布"],
        preview_gradient="linear-gradient(135deg, #0a0a0a 0%, #00ff88 50%, #00d4ff 100%)",
    ),

    # === 渐变紫 ===
    ThemeType.GRADIENT_PURPLE.value: ThemeConfig(
        type=ThemeType.GRADIENT_PURPLE,
        name="渐变紫",
        name_en="Gradient Purple",
        description="紫色渐变现代风格，时尚前卫",
        colors=ThemeColors(
            primary="#7c3aed",
            secondary="#a78bfa",
            accent="#c084fc",
            background="#faf5ff",
            surface="#ffffff",
            text_primary="#3b0764",
            text_secondary="#6b7280",
            border="#e9d5ff",
        ),
        fonts=ThemeFonts(
            title="Poppins, 'Noto Sans SC', sans-serif",
            subtitle="Poppins, 'Noto Sans SC', sans-serif",
            body="Inter, 'Noto Sans SC', sans-serif",
        ),
        style="modern, trendy, gradient",
        recommended_for=["创意产品", "营销活动", "时尚品牌", "互联网产品"],
        preview_gradient="linear-gradient(135deg, #7c3aed 0%, #c084fc 100%)",
    ),

    # === 霓虹未来 ===
    ThemeType.NEON_FUTURE.value: ThemeConfig(
        type=ThemeType.NEON_FUTURE,
        name="霓虹未来",
        name_en="Neon Future",
        description="赛博朋克风格，充满未来感",
        colors=ThemeColors(
            primary="#f0abfc",
            secondary="#22d3ee",
            accent="#facc15",
            background="#18181b",
            surface="#27272a",
            text_primary="#fafafa",
            text_secondary="#a1a1aa",
            border="#3f3f46",
        ),
        fonts=ThemeFonts(
            title="Orbitron, 'Noto Sans SC', sans-serif",
            subtitle="Exo 2, 'Noto Sans SC', sans-serif",
            body="Exo 2, 'Noto Sans SC', sans-serif",
        ),
        style="cyberpunk, neon, bold",
        recommended_for=["游戏", "电竞", "元宇宙", "未来科技"],
        preview_gradient="linear-gradient(135deg, #f0abfc 0%, #22d3ee 50%, #facc15 100%)",
    ),

    # === 极简白 ===
    ThemeType.MINIMAL_WHITE.value: ThemeConfig(
        type=ThemeType.MINIMAL_WHITE,
        name="极简白",
        name_en="Minimal White",
        description="纯净简洁的白色风格，专注内容",
        colors=ThemeColors(
            primary="#18181b",
            secondary="#3f3f46",
            accent="#2563eb",
            background="#ffffff",
            surface="#fafafa",
            text_primary="#18181b",
            text_secondary="#71717a",
            border="#e4e4e7",
        ),
        fonts=ThemeFonts(
            title="Inter, 'Noto Sans SC', sans-serif",
            subtitle="Inter, 'Noto Sans SC', sans-serif",
            body="Inter, 'Noto Sans SC', sans-serif",
        ),
        style="minimal, clean, focused",
        recommended_for=["学术报告", "简洁汇报", "内容为主", "通用场景"],
        preview_gradient="linear-gradient(135deg, #ffffff 0%, #f4f4f5 100%)",
    ),

    # === 自然绿 ===
    ThemeType.NATURE_GREEN.value: ThemeConfig(
        type=ThemeType.NATURE_GREEN,
        name="自然绿",
        name_en="Nature Green",
        description="清新自然的绿色风格，环保健康",
        colors=ThemeColors(
            primary="#15803d",
            secondary="#22c55e",
            accent="#4ade80",
            background="#f0fdf4",
            surface="#ffffff",
            text_primary="#14532d",
            text_secondary="#4b5563",
            border="#bbf7d0",
        ),
        fonts=ThemeFonts(
            title="Nunito, 'Noto Sans SC', sans-serif",
            subtitle="Nunito, 'Noto Sans SC', sans-serif",
            body="Source Sans Pro, 'Noto Sans SC', sans-serif",
        ),
        style="natural, fresh, eco-friendly",
        recommended_for=["环保主题", "健康医疗", "农业食品", "公益项目"],
        preview_gradient="linear-gradient(135deg, #15803d 0%, #4ade80 100%)",
    ),

    # === 柔和粉彩 ===
    ThemeType.SOFT_PASTEL.value: ThemeConfig(
        type=ThemeType.SOFT_PASTEL,
        name="柔和粉彩",
        name_en="Soft Pastel",
        description="温馨柔美的粉彩色调，亲和力强",
        colors=ThemeColors(
            primary="#ec4899",
            secondary="#f472b6",
            accent="#a855f7",
            background="#fdf2f8",
            surface="#ffffff",
            text_primary="#831843",
            text_secondary="#6b7280",
            border="#fbcfe8",
        ),
        fonts=ThemeFonts(
            title="Quicksand, 'Noto Sans SC', sans-serif",
            subtitle="Quicksand, 'Noto Sans SC', sans-serif",
            body="Nunito, 'Noto Sans SC', sans-serif",
        ),
        style="soft, warm, friendly",
        recommended_for=["女性用户", "儿童教育", "美妆时尚", "社交活动"],
        preview_gradient="linear-gradient(135deg, #ec4899 0%, #a855f7 100%)",
    ),

    # === 创意多彩 ===
    ThemeType.CREATIVE_COLORFUL.value: ThemeConfig(
        type=ThemeType.CREATIVE_COLORFUL,
        name="创意多彩",
        name_en="Creative Colorful",
        description="活泼鲜艳的多彩风格，充满活力",
        colors=ThemeColors(
            primary="#ef4444",
            secondary="#f97316",
            accent="#eab308",
            background="#fffbeb",
            surface="#ffffff",
            text_primary="#1c1917",
            text_secondary="#57534e",
            border="#fed7aa",
        ),
        fonts=ThemeFonts(
            title="Poppins, 'Noto Sans SC', sans-serif",
            subtitle="Lato, 'Noto Sans SC', sans-serif",
            body="Lato, 'Noto Sans SC', sans-serif",
        ),
        style="vibrant, playful, energetic",
        recommended_for=["创意提案", "市场营销", "年轻用户", "活动策划"],
        preview_gradient="linear-gradient(135deg, #ef4444 0%, #f97316 50%, #eab308 100%)",
    ),

    # === 暖阳落日 ===
    ThemeType.WARM_SUNSET.value: ThemeConfig(
        type=ThemeType.WARM_SUNSET,
        name="暖阳落日",
        name_en="Warm Sunset",
        description="温暖的橙红色调，温馨舒适",
        colors=ThemeColors(
            primary="#ea580c",
            secondary="#fb923c",
            accent="#fbbf24",
            background="#fff7ed",
            surface="#ffffff",
            text_primary="#431407",
            text_secondary="#78716c",
            border="#fed7aa",
        ),
        fonts=ThemeFonts(
            title="Merriweather, 'Noto Serif SC', serif",
            subtitle="Source Sans Pro, 'Noto Sans SC', sans-serif",
            body="Source Sans Pro, 'Noto Sans SC', sans-serif",
        ),
        style="warm, cozy, inviting",
        recommended_for=["旅游介绍", "美食餐饮", "生活方式", "文化艺术"],
        preview_gradient="linear-gradient(135deg, #ea580c 0%, #fbbf24 100%)",
    ),

    # === 学术经典 ===
    ThemeType.ACADEMIC_CLASSIC.value: ThemeConfig(
        type=ThemeType.ACADEMIC_CLASSIC,
        name="学术经典",
        name_en="Academic Classic",
        description="传统正式的学术风格，严谨专业",
        colors=ThemeColors(
            primary="#1f2937",
            secondary="#4b5563",
            accent="#2563eb",
            background="#f9fafb",
            surface="#ffffff",
            text_primary="#111827",
            text_secondary="#6b7280",
            border="#d1d5db",
        ),
        fonts=ThemeFonts(
            title="Georgia, 'Noto Serif SC', serif",
            subtitle="Georgia, 'Noto Serif SC', serif",
            body="Helvetica, 'Noto Sans SC', sans-serif",
        ),
        style="traditional, formal, academic",
        recommended_for=["学术论文", "研究报告", "教育课程", "毕业答辩"],
        preview_gradient="linear-gradient(135deg, #1f2937 0%, #4b5563 100%)",
    ),

    # ============================================================
    # 二次元/动漫主题
    # ============================================================

    # === 二次元暗黑 ===
    ThemeType.ANIME_DARK.value: ThemeConfig(
        type=ThemeType.ANIME_DARK,
        name="二次元暗黑",
        name_en="Anime Dark",
        description="深色背景配霓虹色，适合动漫/游戏介绍",
        colors=ThemeColors(
            primary="#ff6b9d",  # 樱花粉
            secondary="#c084fc",  # 紫罗兰
            accent="#00f5ff",  # 霓虹青
            background="#0d0d1a",  # 深夜蓝黑
            surface="#1a1a2e",  # 暗紫表面
            text_primary="#f0f0f0",
            text_secondary="#a0a0b0",
            border="#2a2a4a",
        ),
        fonts=ThemeFonts(
            title="'Noto Sans SC', 'M PLUS Rounded 1c', sans-serif",
            subtitle="'Noto Sans SC', sans-serif",
            body="'Noto Sans SC', sans-serif",
        ),
        style="anime, neon, dark, vibrant",
        recommended_for=["动漫介绍", "游戏攻略", "番剧推荐", "二次元活动"],
        preview_gradient="linear-gradient(135deg, #0d0d1a 0%, #ff6b9d 50%, #00f5ff 100%)",
    ),

    # === 二次元可爱 ===
    ThemeType.ANIME_CUTE.value: ThemeConfig(
        type=ThemeType.ANIME_CUTE,
        name="二次元可爱",
        name_en="Anime Cute",
        description="粉彩色系萌系风格，适合日常番/萌系内容",
        colors=ThemeColors(
            primary="#ff9ed2",  # 粉红
            secondary="#b4a7ff",  # 淡紫
            accent="#7dd3fc",  # 天蓝
            background="#fff5f8",  # 浅粉背景
            surface="#ffffff",
            text_primary="#5c4d6e",  # 深紫灰
            text_secondary="#8b7a9e",
            border="#ffd6e7",
        ),
        fonts=ThemeFonts(
            title="'Noto Sans SC', 'Kosugi Maru', sans-serif",
            subtitle="'Noto Sans SC', sans-serif",
            body="'Noto Sans SC', sans-serif",
        ),
        style="cute, pastel, kawaii, soft",
        recommended_for=["萌系动漫", "日常番", "可爱角色", "轻松内容"],
        preview_gradient="linear-gradient(135deg, #ff9ed2 0%, #b4a7ff 50%, #7dd3fc 100%)",
    ),

    # === 赛博朋克 ===
    ThemeType.CYBERPUNK.value: ThemeConfig(
        type=ThemeType.CYBERPUNK,
        name="赛博朋克",
        name_en="Cyberpunk",
        description="紫/青/粉科幻风格，适合机甲/科幻番",
        colors=ThemeColors(
            primary="#f72585",  # 霓虹粉
            secondary="#7209b7",  # 深紫
            accent="#4cc9f0",  # 电光蓝
            background="#10002b",  # 深紫黑
            surface="#240046",  # 暗紫
            text_primary="#e0aaff",  # 淡紫文字
            text_secondary="#9d4edd",
            border="#3c096c",
        ),
        fonts=ThemeFonts(
            title="Orbitron, 'Noto Sans SC', sans-serif",
            subtitle="'Noto Sans SC', sans-serif",
            body="'Noto Sans SC', sans-serif",
        ),
        style="cyberpunk, sci-fi, neon, futuristic",
        recommended_for=["科幻动漫", "机甲番", "赛博朋克", "未来世界"],
        preview_gradient="linear-gradient(135deg, #10002b 0%, #f72585 50%, #4cc9f0 100%)",
    ),

    # === EVA NERV ===
    ThemeType.EVA_NERV.value: ThemeConfig(
        type=ThemeType.EVA_NERV,
        name="EVA NERV",
        name_en="EVA NERV",
        description="新世纪福音战士专用配色，紫/绿/橙经典组合",
        colors=ThemeColors(
            primary="#5B2C6F",  # 初号机紫
            secondary="#1ABC9C",  # 初号机绿
            accent="#E74C3C",  # 贰号机橙红
            background="#1C1C1C",  # NERV 黑
            surface="#2C2C2C",  # 深灰表面
            text_primary="#00FF00",  # 终端绿
            text_secondary="#C0C0C0",  # 银灰
            border="#5B2C6F",
        ),
        fonts=ThemeFonts(
            title="'Noto Sans SC', Impact, sans-serif",
            subtitle="'Noto Sans SC', sans-serif",
            body="'Noto Sans SC', Consolas, monospace",
        ),
        style="eva, nerv, mecha, apocalyptic",
        recommended_for=["EVA", "新世纪福音战士", "机甲动漫", "末世题材"],
        preview_gradient="linear-gradient(135deg, #1C1C1C 0%, #5B2C6F 33%, #1ABC9C 66%, #E74C3C 100%)",
    ),

    # === 复古像素 ===
    ThemeType.RETRO_PIXEL.value: ThemeConfig(
        type=ThemeType.RETRO_PIXEL,
        name="复古像素",
        name_en="Retro Pixel",
        description="8-bit 游戏风格，适合游戏/怀旧内容",
        colors=ThemeColors(
            primary="#ff004d",  # 红
            secondary="#00e436",  # 绿
            accent="#29adff",  # 蓝
            background="#1d2b53",  # 深蓝
            surface="#7e2553",  # 紫红
            text_primary="#fff1e8",  # 米白
            text_secondary="#c2c3c7",  # 浅灰
            border="#ff77a8",  # 粉
        ),
        fonts=ThemeFonts(
            title="'Press Start 2P', 'Noto Sans SC', monospace",
            subtitle="'Noto Sans SC', monospace",
            body="'Noto Sans SC', monospace",
        ),
        style="pixel, retro, 8-bit, gaming",
        recommended_for=["游戏介绍", "复古游戏", "像素艺术", "怀旧内容"],
        preview_gradient="linear-gradient(135deg, #1d2b53 0%, #ff004d 33%, #00e436 66%, #29adff 100%)",
    ),
}


class ThemeService:
    """主题服务"""

    def __init__(self):
        self.themes = THEME_CONFIGS

    def get_all_themes(self) -> List[ThemeConfig]:
        """获取所有主题配置"""
        return list(self.themes.values())

    def get_theme(self, theme_type: str) -> Optional[ThemeConfig]:
        """获取指定主题配置"""
        return self.themes.get(theme_type)

    def get_theme_names(self) -> Dict[str, str]:
        """获取所有主题类型和名称的映射"""
        return {key: config.name for key, config in self.themes.items()}

    def validate_theme(self, theme_type: str) -> bool:
        """验证主题类型是否有效"""
        return theme_type in self.themes

    def suggest_theme(self, scenario: str) -> str:
        """根据场景推荐主题"""
        scenario_lower = scenario.lower()

        # 场景关键词映射 (按优先级排序，更具体的关键词放前面)
        # 使用列表保持顺序
        scenario_keywords = [
            # === 二次元/动漫 (优先匹配，因为更具体) ===
            ("萌系", ThemeType.ANIME_CUTE.value),
            ("萌", ThemeType.ANIME_CUTE.value),
            ("可爱", ThemeType.ANIME_CUTE.value),
            ("日常番", ThemeType.ANIME_CUTE.value),
            ("kawaii", ThemeType.ANIME_CUTE.value),
            ("eva", ThemeType.EVA_NERV.value),
            ("福音战士", ThemeType.EVA_NERV.value),
            ("nerv", ThemeType.EVA_NERV.value),
            ("初号机", ThemeType.EVA_NERV.value),
            ("赛博朋克", ThemeType.CYBERPUNK.value),
            ("cyberpunk", ThemeType.CYBERPUNK.value),
            ("机甲", ThemeType.CYBERPUNK.value),
            ("像素", ThemeType.RETRO_PIXEL.value),
            ("8bit", ThemeType.RETRO_PIXEL.value),
            ("复古", ThemeType.RETRO_PIXEL.value),
            ("动漫", ThemeType.ANIME_DARK.value),
            ("二次元", ThemeType.ANIME_DARK.value),
            ("番剧", ThemeType.ANIME_DARK.value),
            ("anime", ThemeType.ANIME_DARK.value),
            ("acg", ThemeType.ANIME_DARK.value),
            # === 简约 (优先于报告) ===
            ("简洁", ThemeType.MINIMAL_WHITE.value),
            ("简约", ThemeType.MINIMAL_WHITE.value),
            # === 科技 (优先于科幻) ===
            ("科技", ThemeType.DARK_TECH.value),
            ("AI", ThemeType.DARK_TECH.value),
            ("人工智能", ThemeType.DARK_TECH.value),
            ("编程", ThemeType.DARK_TECH.value),
            ("代码", ThemeType.DARK_TECH.value),
            # === 科幻 ===
            ("科幻", ThemeType.CYBERPUNK.value),
            # === 游戏/电竞 ===
            ("游戏", ThemeType.RETRO_PIXEL.value),
            ("电竞", ThemeType.NEON_FUTURE.value),
            # === 商务/企业 ===
            ("商务", ThemeType.MODERN_BUSINESS.value),
            ("企业", ThemeType.CORPORATE_BLUE.value),
            ("正式", ThemeType.CORPORATE_BLUE.value),
            ("报告", ThemeType.CORPORATE_BLUE.value),
            # === 高端 ===
            ("高端", ThemeType.ELEGANT_DARK.value),
            ("奢华", ThemeType.ELEGANT_DARK.value),
            # === 自然/健康 ===
            ("环保", ThemeType.NATURE_GREEN.value),
            ("健康", ThemeType.NATURE_GREEN.value),
            ("自然", ThemeType.NATURE_GREEN.value),
            # === 女性/儿童 ===
            ("女性", ThemeType.SOFT_PASTEL.value),
            ("儿童", ThemeType.SOFT_PASTEL.value),
            # === 创意/营销 ===
            ("创意", ThemeType.CREATIVE_COLORFUL.value),
            ("营销", ThemeType.CREATIVE_COLORFUL.value),
            # === 学术 ===
            ("学术", ThemeType.ACADEMIC_CLASSIC.value),
            ("论文", ThemeType.ACADEMIC_CLASSIC.value),
            ("教育", ThemeType.ACADEMIC_CLASSIC.value),
            ("答辩", ThemeType.ACADEMIC_CLASSIC.value),
            # === 时尚 ===
            ("时尚", ThemeType.GRADIENT_PURPLE.value),
            # === 旅游/美食 ===
            ("旅游", ThemeType.WARM_SUNSET.value),
            ("美食", ThemeType.WARM_SUNSET.value),
        ]

        for keyword, theme in scenario_keywords:
            if keyword in scenario_lower:
                return theme

        # 默认返回现代商务
        return ThemeType.MODERN_BUSINESS.value

    def get_themes_for_scenario(self, scenario: str) -> List[str]:
        """获取适合特定场景的主题列表"""
        scenario_lower = scenario.lower()
        matching_themes = []

        for theme_type, config in self.themes.items():
            for recommended in config.recommended_for:
                if scenario_lower in recommended.lower() or recommended.lower() in scenario_lower:
                    matching_themes.append(theme_type)
                    break

        return matching_themes if matching_themes else [ThemeType.MODERN_BUSINESS.value]

    def generate_theme_css(self, theme_type: str) -> str:
        """生成主题的 CSS 变量"""
        config = self.themes.get(theme_type)
        if not config:
            config = self.themes[ThemeType.MODERN_BUSINESS.value]

        colors = config.colors
        fonts = config.fonts

        return f"""
:root {{
    /* 主题: {config.name} ({config.name_en}) */

    /* 颜色变量 */
    --color-primary: {colors.primary};
    --color-secondary: {colors.secondary};
    --color-accent: {colors.accent};
    --color-background: {colors.background};
    --color-surface: {colors.surface};
    --color-text-primary: {colors.text_primary};
    --color-text-secondary: {colors.text_secondary};
    --color-border: {colors.border};
    --color-success: {colors.success};
    --color-warning: {colors.warning};
    --color-error: {colors.error};

    /* 字体变量 */
    --font-title: {fonts.title};
    --font-subtitle: {fonts.subtitle};
    --font-body: {fonts.body};
    --font-code: {fonts.code};
}}

/* 基础样式 */
body {{
    background-color: var(--color-background);
    color: var(--color-text-primary);
    font-family: var(--font-body);
}}

h1, h2, h3 {{
    font-family: var(--font-title);
    color: var(--color-primary);
}}

h4, h5, h6 {{
    font-family: var(--font-subtitle);
    color: var(--color-secondary);
}}

a {{
    color: var(--color-accent);
}}

code, pre {{
    font-family: var(--font-code);
    background-color: var(--color-surface);
    border: 1px solid var(--color-border);
}}

/* 卡片样式 */
.card {{
    background-color: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: 8px;
}}

/* 按钮样式 */
.btn-primary {{
    background-color: var(--color-primary);
    color: white;
}}

.btn-secondary {{
    background-color: var(--color-secondary);
    color: white;
}}

.btn-accent {{
    background-color: var(--color-accent);
    color: white;
}}
"""

    def generate_reveal_theme_css(self, theme_type: str) -> str:
        """生成 Reveal.js 主题的 CSS"""
        config = self.themes.get(theme_type)
        if not config:
            config = self.themes[ThemeType.MODERN_BUSINESS.value]

        colors = config.colors
        fonts = config.fonts

        return f"""
/* Reveal.js Custom Theme: {config.name} */

.reveal {{
    font-family: {fonts.body};
    font-size: 42px;
    color: {colors.text_primary};
}}

.reveal .slides {{
    text-align: left;
}}

.reveal .slides section {{
    background-color: {colors.background};
}}

.reveal h1 {{
    font-family: {fonts.title};
    color: {colors.primary};
    font-size: 2.5em;
    font-weight: 700;
    margin-bottom: 0.5em;
}}

.reveal h2 {{
    font-family: {fonts.title};
    color: {colors.primary};
    font-size: 1.8em;
    font-weight: 600;
    margin-bottom: 0.5em;
}}

.reveal h3 {{
    font-family: {fonts.subtitle};
    color: {colors.secondary};
    font-size: 1.3em;
    font-weight: 500;
}}

.reveal p {{
    color: {colors.text_primary};
    line-height: 1.6;
}}

.reveal ul, .reveal ol {{
    color: {colors.text_primary};
}}

.reveal li {{
    margin-bottom: 0.5em;
}}

.reveal a {{
    color: {colors.accent};
    text-decoration: none;
}}

.reveal a:hover {{
    color: {colors.secondary};
    text-decoration: underline;
}}

.reveal code {{
    font-family: {fonts.code};
    background-color: {colors.surface};
    padding: 0.2em 0.4em;
    border-radius: 4px;
    font-size: 0.9em;
}}

.reveal pre {{
    background-color: {colors.surface};
    border: 1px solid {colors.border};
    border-radius: 8px;
    padding: 1em;
}}

.reveal blockquote {{
    border-left: 4px solid {colors.accent};
    padding-left: 1em;
    font-style: italic;
    color: {colors.text_secondary};
}}

.reveal table {{
    border-collapse: collapse;
    width: 100%;
}}

.reveal table th {{
    background-color: {colors.primary};
    color: white;
    padding: 0.5em 1em;
}}

.reveal table td {{
    border: 1px solid {colors.border};
    padding: 0.5em 1em;
}}

.reveal table tr:nth-child(even) {{
    background-color: {colors.surface};
}}

/* 强调色块 */
.reveal .highlight {{
    background-color: {colors.accent};
    color: white;
    padding: 0.2em 0.5em;
    border-radius: 4px;
}}

/* 指标卡片 */
.reveal .metric {{
    background-color: {colors.surface};
    border: 1px solid {colors.border};
    border-radius: 12px;
    padding: 1.5em;
    text-align: center;
}}

.reveal .metric .value {{
    font-size: 2.5em;
    font-weight: bold;
    color: {colors.primary};
}}

.reveal .metric .label {{
    font-size: 0.9em;
    color: {colors.text_secondary};
}}
"""


# 全局主题服务实例
@lru_cache()
def get_theme_service() -> ThemeService:
    return ThemeService()


theme_service = get_theme_service()
