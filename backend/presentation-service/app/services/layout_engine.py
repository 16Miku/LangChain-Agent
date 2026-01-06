# ============================================================
# Presentation Service - Layout Engine
# 智能布局引擎 - 支持 15+ 布局类型
# ============================================================

from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel


class LayoutType(str, Enum):
    """布局类型枚举 - 15+ 种布局"""

    # === 基础布局 ===
    TITLE_COVER = "title_cover"          # 封面页 - 大标题 + 副标题 + 作者
    TITLE_SECTION = "title_section"      # 章节页 - 居中大标题
    BULLET_POINTS = "bullet_points"      # 列表页 - 标题 + 3-6 个要点
    TWO_COLUMN = "two_column"            # 双栏布局 - 左文右图/双列表
    IMAGE_TEXT = "image_text"            # 图文混排 - 大图配文字说明

    # === 数据展示 ===
    CHART_SINGLE = "chart_single"        # 单图表 - 标题 + 图表区域
    CHART_DUAL = "chart_dual"            # 双图表对比 - 并排两个图表
    DATA_TABLE = "data_table"            # 数据表格 - 标题 + 表格 + 说明
    METRIC_CARD = "metric_card"          # 指标卡片 - 3-4 个关键指标

    # === 特殊效果 ===
    QUOTE_CENTER = "quote_center"        # 引用页 - 居中引用文字
    TIMELINE = "timeline"                # 时间线 - 垂直/水平时间轴
    PROCESS_FLOW = "process_flow"        # 流程图 - 步骤流程展示
    COMPARISON = "comparison"            # 对比布局 - 左右对比两栏
    GALLERY = "gallery"                  # 图片画廊 - 网格图片展示

    # === 结尾 ===
    THANK_YOU = "thank_you"              # 结尾页 - 感谢 + Q&A
    CONTACT = "contact"                  # 联系方式 - 社交媒体/邮箱/二维码

    # === 新增布局 ===
    BLANK = "blank"                      # 空白页 - 自由内容
    IMAGE_FULL = "image_full"            # 全屏图片 - 背景图 + 叠加文字
    THREE_COLUMN = "three_column"        # 三栏布局 - 三列并排


class LayoutConfig(BaseModel):
    """布局配置"""
    type: LayoutType
    name: str
    description: str
    css_class: str
    supports_images: bool = True
    supports_charts: bool = False
    max_content_length: int = 500
    recommended_for: List[str] = []


# 布局配置字典
LAYOUT_CONFIGS: Dict[str, LayoutConfig] = {
    # === 基础布局 ===
    LayoutType.TITLE_COVER.value: LayoutConfig(
        type=LayoutType.TITLE_COVER,
        name="封面页",
        description="大标题 + 副标题 + 作者信息，适合演示文稿开场",
        css_class="layout-title-cover",
        supports_images=True,
        max_content_length=200,
        recommended_for=["opening", "intro"],
    ),
    LayoutType.TITLE_SECTION.value: LayoutConfig(
        type=LayoutType.TITLE_SECTION,
        name="章节页",
        description="居中大标题，用于分隔不同章节",
        css_class="layout-title-section",
        supports_images=False,
        max_content_length=100,
        recommended_for=["section", "chapter"],
    ),
    LayoutType.BULLET_POINTS.value: LayoutConfig(
        type=LayoutType.BULLET_POINTS,
        name="列表页",
        description="标题 + 3-6 个要点列表，最常用的布局",
        css_class="layout-bullet-points",
        supports_images=True,
        max_content_length=500,
        recommended_for=["content", "points", "features"],
    ),
    LayoutType.TWO_COLUMN.value: LayoutConfig(
        type=LayoutType.TWO_COLUMN,
        name="双栏布局",
        description="左右两栏，可用于图文对照或双列表",
        css_class="layout-two-column",
        supports_images=True,
        max_content_length=400,
        recommended_for=["comparison", "split", "image-text"],
    ),
    LayoutType.IMAGE_TEXT.value: LayoutConfig(
        type=LayoutType.IMAGE_TEXT,
        name="图文混排",
        description="大图配文字说明，突出视觉效果",
        css_class="layout-image-text",
        supports_images=True,
        max_content_length=300,
        recommended_for=["showcase", "product", "feature"],
    ),

    # === 数据展示 ===
    LayoutType.CHART_SINGLE.value: LayoutConfig(
        type=LayoutType.CHART_SINGLE,
        name="单图表",
        description="标题 + 单个图表区域，用于数据可视化",
        css_class="layout-chart-single",
        supports_images=True,
        supports_charts=True,
        max_content_length=200,
        recommended_for=["chart", "data", "statistics"],
    ),
    LayoutType.CHART_DUAL.value: LayoutConfig(
        type=LayoutType.CHART_DUAL,
        name="双图表对比",
        description="并排两个图表，用于数据对比",
        css_class="layout-chart-dual",
        supports_images=True,
        supports_charts=True,
        max_content_length=200,
        recommended_for=["comparison", "dual-data"],
    ),
    LayoutType.DATA_TABLE.value: LayoutConfig(
        type=LayoutType.DATA_TABLE,
        name="数据表格",
        description="标题 + 表格 + 说明文字",
        css_class="layout-data-table",
        supports_images=False,
        max_content_length=600,
        recommended_for=["table", "data", "matrix"],
    ),
    LayoutType.METRIC_CARD.value: LayoutConfig(
        type=LayoutType.METRIC_CARD,
        name="指标卡片",
        description="3-4 个关键指标卡片，突出重要数字",
        css_class="layout-metric-card",
        supports_images=False,
        max_content_length=200,
        recommended_for=["kpi", "metrics", "numbers"],
    ),

    # === 特殊效果 ===
    LayoutType.QUOTE_CENTER.value: LayoutConfig(
        type=LayoutType.QUOTE_CENTER,
        name="引用页",
        description="居中引用文字，突出名言或重点",
        css_class="layout-quote-center",
        supports_images=False,
        max_content_length=200,
        recommended_for=["quote", "highlight", "emphasis"],
    ),
    LayoutType.TIMELINE.value: LayoutConfig(
        type=LayoutType.TIMELINE,
        name="时间线",
        description="垂直或水平时间轴，展示发展历程",
        css_class="layout-timeline",
        supports_images=True,
        max_content_length=400,
        recommended_for=["history", "timeline", "evolution", "roadmap"],
    ),
    LayoutType.PROCESS_FLOW.value: LayoutConfig(
        type=LayoutType.PROCESS_FLOW,
        name="流程图",
        description="步骤流程展示，适合说明操作流程",
        css_class="layout-process-flow",
        supports_images=True,
        max_content_length=400,
        recommended_for=["process", "workflow", "steps", "procedure"],
    ),
    LayoutType.COMPARISON.value: LayoutConfig(
        type=LayoutType.COMPARISON,
        name="对比布局",
        description="左右对比两栏，用于方案对比",
        css_class="layout-comparison",
        supports_images=True,
        max_content_length=400,
        recommended_for=["vs", "comparison", "pros-cons"],
    ),
    LayoutType.GALLERY.value: LayoutConfig(
        type=LayoutType.GALLERY,
        name="图片画廊",
        description="网格图片展示，适合产品展示",
        css_class="layout-gallery",
        supports_images=True,
        max_content_length=200,
        recommended_for=["gallery", "portfolio", "products"],
    ),

    # === 结尾 ===
    LayoutType.THANK_YOU.value: LayoutConfig(
        type=LayoutType.THANK_YOU,
        name="结尾页",
        description="感谢 + Q&A，演示结束页",
        css_class="layout-thank-you",
        supports_images=False,
        max_content_length=150,
        recommended_for=["ending", "thanks", "qa"],
    ),
    LayoutType.CONTACT.value: LayoutConfig(
        type=LayoutType.CONTACT,
        name="联系方式",
        description="社交媒体/邮箱/二维码",
        css_class="layout-contact",
        supports_images=True,
        max_content_length=200,
        recommended_for=["contact", "social", "info"],
    ),

    # === 新增布局 ===
    LayoutType.BLANK.value: LayoutConfig(
        type=LayoutType.BLANK,
        name="空白页",
        description="自由内容布局，无固定结构",
        css_class="layout-blank",
        supports_images=True,
        max_content_length=800,
        recommended_for=["custom", "free"],
    ),
    LayoutType.IMAGE_FULL.value: LayoutConfig(
        type=LayoutType.IMAGE_FULL,
        name="全屏图片",
        description="背景图 + 叠加文字，视觉冲击力强",
        css_class="layout-image-full",
        supports_images=True,
        max_content_length=100,
        recommended_for=["impact", "hero", "showcase"],
    ),
    LayoutType.THREE_COLUMN.value: LayoutConfig(
        type=LayoutType.THREE_COLUMN,
        name="三栏布局",
        description="三列并排，适合功能对比或多项展示",
        css_class="layout-three-column",
        supports_images=True,
        max_content_length=450,
        recommended_for=["features", "options", "tiers"],
    ),
}


class LayoutEngine:
    """智能布局引擎"""

    def __init__(self):
        self.layouts = LAYOUT_CONFIGS

    def get_all_layouts(self) -> List[LayoutConfig]:
        """获取所有布局配置"""
        return list(self.layouts.values())

    def get_layout(self, layout_type: str) -> Optional[LayoutConfig]:
        """获取指定布局配置"""
        return self.layouts.get(layout_type)

    def get_layout_names(self) -> Dict[str, str]:
        """获取所有布局类型和名称的映射"""
        return {key: config.name for key, config in self.layouts.items()}

    def suggest_layout(self, content_type: str) -> str:
        """根据内容类型推荐布局"""
        content_type_lower = content_type.lower()

        for layout_type, config in self.layouts.items():
            if content_type_lower in config.recommended_for:
                return layout_type

        # 默认返回列表页
        return LayoutType.BULLET_POINTS.value

    def suggest_layouts_for_presentation(
        self,
        slide_count: int,
        has_data: bool = False,
        has_timeline: bool = False,
        has_comparison: bool = False,
    ) -> List[str]:
        """
        为整个演示文稿推荐布局序列

        Args:
            slide_count: 幻灯片数量
            has_data: 是否包含数据图表
            has_timeline: 是否包含时间线内容
            has_comparison: 是否包含对比内容

        Returns:
            推荐的布局类型列表
        """
        layouts = []

        # 第一页固定为封面
        layouts.append(LayoutType.TITLE_COVER.value)

        # 中间页面根据内容类型推荐
        remaining = slide_count - 2  # 减去封面和结尾

        if remaining > 0:
            # 添加一个章节页（如果幻灯片数量足够）
            if slide_count >= 5:
                layouts.append(LayoutType.TITLE_SECTION.value)
                remaining -= 1

        # 填充中间内容页
        content_layouts = [LayoutType.BULLET_POINTS.value]

        if has_data:
            content_layouts.extend([
                LayoutType.CHART_SINGLE.value,
                LayoutType.METRIC_CARD.value,
            ])

        if has_timeline:
            content_layouts.append(LayoutType.TIMELINE.value)

        if has_comparison:
            content_layouts.extend([
                LayoutType.COMPARISON.value,
                LayoutType.TWO_COLUMN.value,
            ])

        # 循环添加内容布局
        for i in range(remaining):
            layouts.append(content_layouts[i % len(content_layouts)])

        # 最后一页固定为结尾
        layouts.append(LayoutType.THANK_YOU.value)

        return layouts

    def generate_layout_css(self, theme: str = "modern_business") -> str:
        """
        生成布局的 CSS 样式

        Args:
            theme: 主题名称

        Returns:
            CSS 样式字符串
        """
        return f"""
/* ============================================
   布局引擎 CSS - 支持 {len(self.layouts)} 种布局
   主题: {theme}
   ============================================ */

/* === 基础布局 === */

/* 封面页 */
.layout-title-cover {{
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    min-height: 100%;
}}
.layout-title-cover h1 {{
    font-size: 2.5em;
    margin-bottom: 0.5em;
}}
.layout-title-cover .subtitle {{
    font-size: 1.2em;
    opacity: 0.8;
}}

/* 章节页 */
.layout-title-section {{
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
}}
.layout-title-section h1 {{
    font-size: 2em;
    border-bottom: 3px solid currentColor;
    padding-bottom: 0.3em;
}}

/* 列表页 */
.layout-bullet-points ul {{
    text-align: left;
    margin-left: 1em;
}}
.layout-bullet-points li {{
    margin-bottom: 0.5em;
    font-size: 1.1em;
}}

/* 双栏布局 */
.layout-two-column {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2em;
    align-items: start;
}}
.layout-two-column .column {{
    padding: 1em;
}}

/* 三栏布局 */
.layout-three-column {{
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 1.5em;
    align-items: start;
}}
.layout-three-column .column {{
    padding: 0.8em;
    text-align: center;
}}

/* 图文混排 */
.layout-image-text {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2em;
    align-items: center;
}}
.layout-image-text img {{
    max-width: 100%;
    border-radius: 8px;
}}

/* 全屏图片 */
.layout-image-full {{
    position: relative;
    background-size: cover;
    background-position: center;
}}
.layout-image-full .overlay {{
    position: absolute;
    bottom: 2em;
    left: 2em;
    background: rgba(0, 0, 0, 0.6);
    padding: 1em 2em;
    border-radius: 8px;
    color: white;
}}

/* === 数据展示 === */

/* 单图表 */
.layout-chart-single {{
    display: flex;
    flex-direction: column;
    align-items: center;
}}
.layout-chart-single .chart-container {{
    width: 80%;
    max-width: 600px;
    margin: 1em auto;
}}

/* 双图表 */
.layout-chart-dual {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2em;
}}
.layout-chart-dual .chart-container {{
    width: 100%;
}}

/* 数据表格 */
.layout-data-table table {{
    width: 100%;
    border-collapse: collapse;
    margin: 1em 0;
}}
.layout-data-table th,
.layout-data-table td {{
    border: 1px solid currentColor;
    padding: 0.5em 1em;
    text-align: left;
}}
.layout-data-table th {{
    background: rgba(0, 0, 0, 0.1);
    font-weight: bold;
}}

/* 指标卡片 */
.layout-metric-card {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1.5em;
    text-align: center;
}}
.layout-metric-card .card {{
    padding: 1.5em;
    background: rgba(0, 0, 0, 0.05);
    border-radius: 12px;
}}
.layout-metric-card .card .value {{
    font-size: 2.5em;
    font-weight: bold;
    color: var(--primary-color, #3b82f6);
}}
.layout-metric-card .card .label {{
    font-size: 0.9em;
    opacity: 0.8;
    margin-top: 0.5em;
}}

/* === 特殊效果 === */

/* 引用页 */
.layout-quote-center {{
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    font-style: italic;
}}
.layout-quote-center blockquote {{
    font-size: 1.5em;
    max-width: 80%;
    border-left: 4px solid currentColor;
    padding-left: 1em;
    margin: 0;
}}
.layout-quote-center .author {{
    margin-top: 1em;
    font-size: 1em;
    font-style: normal;
    opacity: 0.8;
}}

/* 时间线 */
.layout-timeline {{
    position: relative;
    padding-left: 2em;
}}
.layout-timeline::before {{
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 3px;
    background: currentColor;
    opacity: 0.3;
}}
.layout-timeline .event {{
    position: relative;
    padding-bottom: 1.5em;
    padding-left: 1.5em;
}}
.layout-timeline .event::before {{
    content: '';
    position: absolute;
    left: -2.35em;
    top: 0.3em;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: currentColor;
}}
.layout-timeline .event .date {{
    font-weight: bold;
    color: var(--primary-color, #3b82f6);
}}

/* 流程图 */
.layout-process-flow {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 1em;
}}
.layout-process-flow .step {{
    flex: 1;
    min-width: 120px;
    text-align: center;
    padding: 1em;
    background: rgba(0, 0, 0, 0.05);
    border-radius: 8px;
    position: relative;
}}
.layout-process-flow .step:not(:last-child)::after {{
    content: '→';
    position: absolute;
    right: -0.8em;
    top: 50%;
    transform: translateY(-50%);
    font-size: 1.5em;
    opacity: 0.5;
}}
.layout-process-flow .step .number {{
    display: inline-block;
    width: 2em;
    height: 2em;
    line-height: 2em;
    border-radius: 50%;
    background: var(--primary-color, #3b82f6);
    color: white;
    font-weight: bold;
    margin-bottom: 0.5em;
}}

/* 对比布局 */
.layout-comparison {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2em;
}}
.layout-comparison .side {{
    padding: 1.5em;
    border-radius: 12px;
}}
.layout-comparison .side-left {{
    background: rgba(34, 197, 94, 0.1);
    border-left: 4px solid #22c55e;
}}
.layout-comparison .side-right {{
    background: rgba(239, 68, 68, 0.1);
    border-left: 4px solid #ef4444;
}}
.layout-comparison .side h3 {{
    margin-top: 0;
}}

/* 图片画廊 */
.layout-gallery {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1em;
}}
.layout-gallery .gallery-item {{
    aspect-ratio: 4/3;
    overflow: hidden;
    border-radius: 8px;
}}
.layout-gallery .gallery-item img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s;
}}
.layout-gallery .gallery-item:hover img {{
    transform: scale(1.05);
}}

/* === 结尾 === */

/* 结尾页 */
.layout-thank-you {{
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
}}
.layout-thank-you h1 {{
    font-size: 2.5em;
    margin-bottom: 0.5em;
}}
.layout-thank-you .qa {{
    font-size: 1.2em;
    opacity: 0.8;
    margin-top: 1em;
}}

/* 联系方式页 */
.layout-contact {{
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
}}
.layout-contact .contact-info {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 2em;
    margin-top: 2em;
    width: 100%;
    max-width: 600px;
}}
.layout-contact .contact-item {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5em;
}}
.layout-contact .contact-item .icon {{
    font-size: 2em;
}}

/* 空白页 */
.layout-blank {{
    padding: 2em;
}}
"""

    def get_layout_html_template(self, layout_type: str) -> str:
        """
        获取布局的 HTML 模板

        Args:
            layout_type: 布局类型

        Returns:
            HTML 模板字符串
        """
        templates = {
            LayoutType.TITLE_COVER.value: """
<section class="layout-title-cover">
    <h1>{title}</h1>
    <p class="subtitle">{subtitle}</p>
    <p class="author">{author}</p>
</section>
""",
            LayoutType.TITLE_SECTION.value: """
<section class="layout-title-section">
    <h1>{title}</h1>
</section>
""",
            LayoutType.BULLET_POINTS.value: """
<section class="layout-bullet-points">
    <h2>{title}</h2>
    <ul>
        {content}
    </ul>
</section>
""",
            LayoutType.TWO_COLUMN.value: """
<section class="layout-two-column">
    <div class="column left">
        <h3>{left_title}</h3>
        {left_content}
    </div>
    <div class="column right">
        <h3>{right_title}</h3>
        {right_content}
    </div>
</section>
""",
            LayoutType.THREE_COLUMN.value: """
<section class="layout-three-column">
    <div class="column">
        <h3>{col1_title}</h3>
        {col1_content}
    </div>
    <div class="column">
        <h3>{col2_title}</h3>
        {col2_content}
    </div>
    <div class="column">
        <h3>{col3_title}</h3>
        {col3_content}
    </div>
</section>
""",
            LayoutType.IMAGE_TEXT.value: """
<section class="layout-image-text">
    <div class="image">
        <img src="{image_url}" alt="{image_alt}">
    </div>
    <div class="text">
        <h2>{title}</h2>
        {content}
    </div>
</section>
""",
            LayoutType.IMAGE_FULL.value: """
<section class="layout-image-full" style="background-image: url('{background_image}');">
    <div class="overlay">
        <h2>{title}</h2>
        <p>{content}</p>
    </div>
</section>
""",
            LayoutType.CHART_SINGLE.value: """
<section class="layout-chart-single">
    <h2>{title}</h2>
    <div class="chart-container">
        {chart}
    </div>
    <p class="description">{description}</p>
</section>
""",
            LayoutType.CHART_DUAL.value: """
<section class="layout-chart-dual">
    <div class="chart-container">
        <h3>{left_title}</h3>
        {left_chart}
    </div>
    <div class="chart-container">
        <h3>{right_title}</h3>
        {right_chart}
    </div>
</section>
""",
            LayoutType.DATA_TABLE.value: """
<section class="layout-data-table">
    <h2>{title}</h2>
    <table>
        {table_content}
    </table>
    <p class="note">{note}</p>
</section>
""",
            LayoutType.METRIC_CARD.value: """
<section class="layout-metric-card">
    <h2>{title}</h2>
    <div class="cards">
        {cards}
    </div>
</section>
""",
            LayoutType.QUOTE_CENTER.value: """
<section class="layout-quote-center">
    <blockquote>{quote}</blockquote>
    <p class="author">— {author}</p>
</section>
""",
            LayoutType.TIMELINE.value: """
<section class="layout-timeline">
    <h2>{title}</h2>
    <div class="events">
        {events}
    </div>
</section>
""",
            LayoutType.PROCESS_FLOW.value: """
<section class="layout-process-flow">
    <h2>{title}</h2>
    <div class="steps">
        {steps}
    </div>
</section>
""",
            LayoutType.COMPARISON.value: """
<section class="layout-comparison">
    <h2>{title}</h2>
    <div class="sides">
        <div class="side side-left">
            <h3>{left_title}</h3>
            {left_content}
        </div>
        <div class="side side-right">
            <h3>{right_title}</h3>
            {right_content}
        </div>
    </div>
</section>
""",
            LayoutType.GALLERY.value: """
<section class="layout-gallery">
    <h2>{title}</h2>
    <div class="gallery-grid">
        {images}
    </div>
</section>
""",
            LayoutType.THANK_YOU.value: """
<section class="layout-thank-you">
    <h1>{title}</h1>
    <p class="qa">{content}</p>
</section>
""",
            LayoutType.CONTACT.value: """
<section class="layout-contact">
    <h2>{title}</h2>
    <div class="contact-info">
        {contact_items}
    </div>
</section>
""",
            LayoutType.BLANK.value: """
<section class="layout-blank">
    <h2>{title}</h2>
    <div class="content">
        {content}
    </div>
</section>
""",
        }

        return templates.get(layout_type, templates[LayoutType.BULLET_POINTS.value])

    def validate_layout(self, layout_type: str) -> bool:
        """验证布局类型是否有效"""
        return layout_type in self.layouts

    def get_compatible_layouts(self, content_length: int, has_images: bool = False) -> List[str]:
        """
        根据内容长度和是否有图片获取兼容的布局列表

        Args:
            content_length: 内容长度
            has_images: 是否包含图片

        Returns:
            兼容的布局类型列表
        """
        compatible = []

        for layout_type, config in self.layouts.items():
            if content_length <= config.max_content_length:
                if not has_images or config.supports_images:
                    compatible.append(layout_type)

        return compatible


# 全局布局引擎实例
layout_engine = LayoutEngine()
