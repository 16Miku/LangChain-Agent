# ============================================================
# Presentation Service - Export Service
# 演示文稿导出服务 (HTML/PDF)
# ============================================================

import base64
from typing import Optional, Dict, Any
from datetime import datetime


class ExportService:
    """
    演示文稿导出服务

    支持:
    - HTML 导出 (完整独立网页)
    - PDF 导出 (需要外部库支持)
    """

    def __init__(self):
        pass

    async def export_to_html(
        self,
        presentation: Dict[str, Any],
        include_reveal_js: bool = True,
        theme_css: Optional[str] = None,
    ) -> str:
        """
        导出演示文稿为 HTML

        Args:
            presentation: 演示文稿数据
            include_reveal_js: 是否包含 Reveal.js 库 (CDN)
            theme_css: 自定义主题 CSS

        Returns:
            HTML 字符串
        """
        title = presentation.get("title", "演示文稿")
        slides = presentation.get("slides", [])
        theme = presentation.get("theme", "modern_business")

        # 如果没有提供主题 CSS，获取默认主题样式
        if not theme_css:
            from app.services.theme_service import theme_service
            theme_css = theme_service.generate_reveal_theme_css(theme)

        # 生成幻灯片 HTML
        slides_html = self._generate_slides_html(slides)

        # 根据 include_reveal_js 参数生成不同的 HTML
        if include_reveal_js:
            html = self._generate_reveal_html(title, presentation, theme_css, slides_html)
        else:
            html = self._generate_simple_html(title, presentation, theme_css, slides_html)

        return html

    def _generate_reveal_html(
        self,
        title: str,
        presentation: Dict[str, Any],
        theme_css: str,
        slides_html: str,
    ) -> str:
        """生成包含 Reveal.js 的完整 HTML"""
        description = presentation.get("description", "")

        # 生成完整 HTML
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self._escape_html(title)}</title>
    <meta name="description" content="{self._escape_html(description)}">
    <meta name="generator" content="Stream-Agent Presentation Service">

    <!-- Reveal.js CSS -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.5.0/reveal.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.5.0/theme/white.min.css">

    <!-- Custom Theme -->
    <style>
        {theme_css}

        /* 额外自定义样式 */
        .reveal .slides section {{
            text-align: left;
        }}

        .reveal h1, .reveal h2, .reveal h3 {{
            text-transform: none;
        }}

        .reveal ul {{
            display: block;
        }}

        .reveal ul li {{
            margin-bottom: 0.5em;
        }}

        /* 图片样式 */
        .reveal img {{
            max-width: 100%;
            max-height: 60vh;
            margin: 1rem auto;
        }}

        /* 代码块样式 */
        .reveal pre {{
            box-shadow: none;
        }}

        /* 表格样式 */
        .reveal table {{
            margin: 1rem auto;
            border-collapse: collapse;
        }}

        .reveal table th,
        .reveal table td {{
            padding: 0.5rem 1rem;
            border: 1px solid #ddd;
        }}

        .reveal table th {{
            background: rgba(0, 0, 0, 0.1);
        }}

        /* 页脚信息 */
        .footer {{
            position: fixed;
            bottom: 20px;
            left: 20px;
            font-size: 12px;
            color: #888;
            z-index: 1000;
        }}

        /* 封面页特殊样式 */
        .reveal .title-cover {{
            text-align: center;
        }}

        .reveal .title-cover h1 {{
            font-size: 2.5em;
            margin-bottom: 0.5em;
        }}

        /* 感谢页样式 */
        .reveal .thank-you {{
            text-align: center;
        }}

        /* 指标卡片样式 */
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }}

        .metric {{
            background: rgba(0, 0, 0, 0.05);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
        }}

        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }}

        .metric-label {{
            font-size: 0.9em;
            opacity: 0.8;
        }}

        /* 图片网格样式 */
        .image-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 1rem 0;
        }}

        .image-grid img {{
            width: 100%;
            border-radius: 8px;
        }}

        /* 两栏布局 */
        .two-column {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            align-items: center;
        }}

        /* 三栏布局 */
        .three-column {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1.5rem;
        }}

        @media (max-width: 768px) {{
            .two-column,
            .three-column {{
                grid-template-columns: 1fr;
            }}
        }}

        /* 时间线样式 */
        .timeline {{
            position: relative;
            padding-left: 2rem;
            margin: 2rem 0;
        }}

        .timeline::before {{
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 2px;
            background: currentColor;
            opacity: 0.3;
        }}

        .timeline-item {{
            position: relative;
            padding-bottom: 1.5rem;
        }}

        .timeline-item::before {{
            content: '';
            position: absolute;
            left: -2.4rem;
            top: 0.3rem;
            width: 1rem;
            height: 1rem;
            border-radius: 50%;
            background: currentColor;
        }}

        /* 流程图样式 */
        .flow-steps {{
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 1rem;
            margin: 2rem 0;
        }}

        .flow-step {{
            background: rgba(0, 0, 0, 0.05);
            padding: 1rem 1.5rem;
            border-radius: 8px;
            position: relative;
        }}

        .flow-step:not(:last-child)::after {{
            content: '→';
            position: absolute;
            right: -1.2rem;
            top: 50%;
            transform: translateY(-50%);
            font-size: 1.5rem;
        }}

        /* 引用样式 */
        .quote-block {{
            font-size: 1.5em;
            font-style: italic;
            text-align: center;
            padding: 2rem;
            margin: 2rem auto;
            max-width: 80%;
            border-left: 4px solid currentColor;
        }}

        /* 对比布局 */
        .comparison {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
        }}

        .comparison-column {{
            padding: 1.5rem;
            border-radius: 12px;
        }}

        .comparison-left {{
            background: rgba(59, 130, 246, 0.1);
        }}

        .comparison-right {{
            background: rgba(34, 197, 94, 0.1);
        }}
    </style>
</head>
<body>
    <div class="reveal">
        <div class="slides">
{slides_html}
        </div>
    </div>

    <!-- Reveal.js -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.5.0/reveal.min.js"></script>

    <!-- Reveal.js Plugins -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.5.0/plugin/notes/notes.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.5.0/plugin/markdown/markdown.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.5.0/plugin/highlight/highlight.min.js"></script>

    <script>
        // 初始化 Reveal.js
        Reveal.initialize({{
            hash: true,
            center: true,
            controls: true,
            progress: true,
            slideNumber: true,
            keyboard: true,
            overview: true,
            touch: true,
            loop: false,
            rtl: false,
            shuffle: false,
            fragments: true,
            embedded: false,
            help: true,
            showNotes: false,
            autoPlayMedia: false,
            preloadIframes: null,
            autoAnimate: true,
            autoAnimateMatcher: null,
            autoAnimateEasing: 'ease',
            autoAnimateDuration: 1000,
            autoAnimateUnmatched: true,
            autoAnimateStyles: [
                'opacity',
                'color',
                'background-color',
                'padding',
                'font-size'
            ],
            transition: 'slide',
            transitionSpeed: 'default',
            backgroundTransition: 'fade',
            parallaxBackgroundImage: '',
            parallaxBackgroundSize: '',
            parallaxBackgroundHorizontal: null,
            parallaxBackgroundVertical: null,
            pdfMaxPagesPerSlide: Number.POSITIVE_INFINITY,
            pdfSeparateFragments: true,
            pdfPageHeightOffset: -1,

            // 插件配置
            plugins: [ RevealNotes, RevealMarkdown, RevealHighlight ]
        }});

        // 导出时间戳
        console.log('Presentation exported: {datetime.now().isoformat()}');
        console.log('Generated by Stream-Agent Presentation Service');
    </script>

    <div class="footer">
        Generated by Stream-Agent | {datetime.now().strftime('%Y-%m-%d %H:%M')}
    </div>
</body>
</html>
"""
        return html

    def _generate_simple_html(
        self,
        title: str,
        presentation: Dict[str, Any],
        theme_css: str,
        slides_html: str,
    ) -> str:
        """生成简单的 HTML (不含 Reveal.js)"""
        description = presentation.get("description", "")

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self._escape_html(title)}</title>
    <meta name="description" content="{self._escape_html(description)}">
    <meta name="generator" content="Stream-Agent Presentation Service">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            background: #f8f9fa;
        }}

        .slide {{
            background: white;
            border-radius: 8px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            page-break-after: always;
        }}

        h1 {{
            color: #1e3a8a;
            border-bottom: 2px solid #3b82f6;
            padding-bottom: 0.5rem;
        }}

        h2 {{
            color: #0369a1;
            margin-top: 1.5rem;
        }}

        ul {{
            padding-left: 1.5rem;
        }}

        li {{
            margin-bottom: 0.5rem;
        }}

        img {{
            max-width: 100%;
            border-radius: 8px;
        }}

        .footer {{
            text-align: center;
            color: #64748b;
            font-size: 0.875rem;
            margin-top: 2rem;
        }}

        {theme_css.replace('.reveal', '')}
    </style>
</head>
<body>
{slides_html}
    <div class="footer">
        Generated by Stream-Agent | {datetime.now().strftime('%Y-%m-%d %H:%M')}
    </div>
</body>
</html>
"""
        return html

    def _generate_slides_html(self, slides: list) -> str:
        """生成幻灯片 HTML"""
        slides_html = []

        for i, slide in enumerate(slides):
            slide_html = self._generate_slide_html(slide, i)
            slides_html.append(f"            {slide_html}")

        return "\n".join(slides_html)

    def _generate_slide_html(self, slide: dict, index: int) -> str:
        """生成单个幻灯片 HTML"""
        layout = slide.get("layout", "bullet_points")
        title = self._escape_html(slide.get("title", ""))
        content = slide.get("content", "")
        notes = slide.get("notes", "")
        images = slide.get("images", [])
        background = slide.get("background")

        # 背景样式
        bg_style = ""
        if background:
            if background.startswith("#") or background.startswith("rgb"):
                bg_style = f' style="background-color: {background}"'
            elif background.startswith("http"):
                bg_style = f' style="background-image: url({background}); background-size: cover; background-position: center;"'

        # 开始标签
        html = f'<section data-layout="{layout}"{bg_style}>\n'

        # 标题 - 封面页使用 h1，其他页面使用 h2
        if title:
            if layout == "title_cover":
                html += f"                <h1>{title}</h1>\n"
            else:
                html += f"                <h2>{title}</h2>\n"

        # 根据布局生成内容
        html += self._generate_content_by_layout(layout, content, images, slide)

        # 演讲者备注
        if notes:
            html += f'                <aside class="notes">{self._escape_html(notes)}</aside>\n'

        html += "            </section>"

        return html

    def _generate_content_by_layout(
        self, layout: str, content: str, images: list, slide: dict
    ) -> str:
        """根据布局类型生成内容 HTML"""
        from app.services.layout_engine import LayoutType

        html = ""

        # 处理图片
        if images:
            image_html = self._generate_images_html(images)
        else:
            image_html = ""

        # 根据布局类型处理
        if layout == LayoutType.TITLE_COVER.value:
            # 封面页
            html = f'                <div class="title-cover">\n'
            html += f"                    {self._markdown_to_html(content)}\n"
            html += f"                    {image_html}\n"
            html += f'                </div>\n'

        elif layout == LayoutType.TITLE_SECTION.value:
            # 章节页
            html = f'                <div class="title-section">\n'
            html += f"                    {self._markdown_to_html(content)}\n"
            html += f'                </div>\n'

        elif layout == LayoutType.IMAGE_FULL.value:
            # 全屏图片
            html = f"                    {image_html}\n"

        elif layout == LayoutType.TWO_COLUMN.value:
            # 双栏布局
            html = f'                <div class="two-column">\n'
            # 如果有图片，左侧内容右侧图片；否则将内容分成两列
            if image_html:
                html += f'                    <div>\n{self._markdown_to_html(content)}\n                    </div>\n'
                html += f'                    <div>\n{image_html}\n                    </div>\n'
            else:
                parts = self._split_content_for_columns(content, 2)
                html += f'                    <div>\n{self._markdown_to_html(parts[0])}\n                    </div>\n'
                html += f'                    <div>\n{self._markdown_to_html(parts[1] if len(parts) > 1 else "")}\n                    </div>\n'
            html += f'                </div>\n'

        elif layout == LayoutType.THREE_COLUMN.value:
            # 三栏布局
            html = f'                <div class="three-column">\n'
            # 尝试将内容按列分割
            parts = self._split_content_for_columns(content, 3)
            for part in parts:
                html += f'                    <div>\n{self._markdown_to_html(part)}\n                    </div>\n'
            html += f'                </div>\n'

        elif layout == LayoutType.METRIC_CARD.value:
            # 指标卡片
            html = f"                    {self._generate_metric_cards(content)}\n"

        elif layout == LayoutType.GALLERY.value:
            # 图片画廊
            html = f'                <div class="image-grid">\n'
            html += f"                    {image_html}\n"
            html += f"                    {self._markdown_to_html(content)}\n"
            html += f'                </div>\n'

        elif layout == LayoutType.TIMELINE.value:
            # 时间线
            html = f'                <div class="timeline">\n'
            html += f"                    {self._generate_timeline(content)}\n"
            html += f'                </div>\n'

        elif layout == LayoutType.PROCESS_FLOW.value:
            # 流程图
            html = f'                <div class="flow-steps">\n'
            html += f"                    {self._generate_flow_steps(content)}\n"
            html += f'                </div>\n'

        elif layout == LayoutType.COMPARISON.value:
            # 对比布局
            html = f'                <div class="comparison">\n'
            parts = self._split_content_for_columns(content, 2)
            html += f'                    <div class="comparison-column comparison-left">\n'
            html += f"                        {self._markdown_to_html(parts[0] if parts else content)}\n"
            html += f'                    </div>\n'
            html += f'                    <div class="comparison-column comparison-right">\n'
            html += f"                        {self._markdown_to_html(parts[1] if len(parts) > 1 else '')}\n"
            html += f'                    </div>\n'
            html += f'                </div>\n'

        elif layout == LayoutType.QUOTE_CENTER.value:
            # 引用页
            html = f'                <div class="quote-block">\n'
            html += f"                    {self._escape_html(content)}\n"
            html += f'                </div>\n'

        elif layout == LayoutType.THANK_YOU.value:
            # 感谢页
            html = f'                <div class="thank-you">\n'
            html += f"                    {self._markdown_to_html(content)}\n"
            html += f'                </div>\n'

        elif layout == LayoutType.BLANK.value:
            # 空白页，不添加内容
            html = ""

        else:
            # 默认：列表布局
            html = f"                    {self._markdown_to_html(content)}\n"
            if image_html:
                html += f"                    {image_html}\n"

        return html

    def _generate_images_html(self, images: list) -> str:
        """生成图片 HTML"""
        if not images:
            return ""

        html = ""
        for img in images:
            url = img.get("url", "")
            caption = img.get("caption", "")
            alt = img.get("alt", "")

            if url:
                # 检查是否为 base64 图片
                if url.startswith("data:image"):
                    html += f'<img src="{url}" alt="{self._escape_html(alt or caption)}" />\n'
                else:
                    html += f'<img src="{url}" alt="{self._escape_html(alt or caption)}" />\n'

                if caption:
                    html += f'<p class="caption" style="font-size: 0.8em; opacity: 0.7;">{self._escape_html(caption)}</p>\n'

        return html

    def _generate_metric_cards(self, content: str) -> str:
        """生成指标卡片 HTML"""
        # 尝试从内容中提取指标
        # 格式: "## 指标1: 100\n## 指标2: 200"
        lines = content.split("\n")
        metrics = []

        for line in lines:
            line = line.strip()
            if ":" in line and not line.startswith("#"):
                parts = line.split(":", 1)
                if len(parts) == 2:
                    label = parts[0].strip()
                    value = parts[1].strip()
                    metrics.append((label, value))

        if metrics:
            html = '<div class="metric-grid">\n'
            for label, value in metrics:
                html += f'                    <div class="metric">\n'
                html += f'                        <div class="metric-value">{self._escape_html(value)}</div>\n'
                html += f'                        <div class="metric-label">{self._escape_html(label)}</div>\n'
                html += f'                    </div>\n'
            html += '                    </div>\n'
            return html
        else:
            # 如果无法解析，返回普通内容
            return self._markdown_to_html(content)

    def _generate_timeline(self, content: str) -> str:
        """生成时间线 HTML"""
        lines = content.split("\n")
        html = ""

        for line in lines:
            line = line.strip()
            if line:
                # 尝试解析时间线项目
                if " - " in line or "：" in line or ":" in line:
                    html += f'                    <div class="timeline-item">\n'
                    html += f"                        {self._markdown_to_html(line)}\n"
                    html += f'                    </div>\n'
                else:
                    html += f'                    <div class="timeline-item">{self._escape_html(line)}</div>\n'

        return html

    def _generate_flow_steps(self, content: str) -> str:
        """生成流程步骤 HTML"""
        # 按行分割步骤
        lines = [line.strip() for line in content.split("\n") if line.strip()]

        html = ""
        for line in lines:
            # 移除序号
            step = line
            if line.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.")):
                step = line.split(".", 1)[1].strip() if "." in line else line
            elif line.startswith(("1、", "2、", "3、", "4、", "5、")):
                step = line.split("、", 1)[1].strip() if "、" in line else line

            html += f'                    <div class="flow-step">{self._escape_html(step)}</div>\n'

        return html

    def _split_content_for_columns(self, content: str, num_columns: int) -> list:
        """将内容分割成多列"""
        lines = content.split("\n")
        # 按标题或空行分割
        sections = []
        current_section = []

        for line in lines:
            if line.strip() == "" or line.strip().startswith("#"):
                if current_section:
                    sections.append("\n".join(current_section))
                    current_section = []
                if line.strip():
                    current_section.append(line)
            else:
                current_section.append(line)

        if current_section:
            sections.append("\n".join(current_section))

        # 如果没有分割成功，按行数分割
        if len(sections) <= 1:
            lines = [line for line in lines if line.strip()]
            chunk_size = max(1, len(lines) // num_columns)
            sections = []
            for i in range(0, len(lines), chunk_size):
                sections.append("\n".join(lines[i:i + chunk_size]))

        # 确保返回指定数量的列
        while len(sections) < num_columns:
            sections.append("")

        return sections[:num_columns]

    def _markdown_to_html(self, markdown: str) -> str:
        """简单的 Markdown 转 HTML"""
        if not markdown:
            return ""

        # 先处理字面量 \n 转换为实际换行符
        markdown = markdown.replace("\\n", "\n")

        lines = markdown.split("\n")
        result = []
        in_list = False

        for line in lines:
            stripped = line.strip()

            # 标题
            if stripped.startswith("### "):
                if in_list:
                    result.append("</ul>")
                    in_list = False
                result.append(f"<h3>{self._escape_html(stripped[4:])}</h3>")
            elif stripped.startswith("## "):
                if in_list:
                    result.append("</ul>")
                    in_list = False
                result.append(f"<h2>{self._escape_html(stripped[3:])}</h2>")
            elif stripped.startswith("# "):
                if in_list:
                    result.append("</ul>")
                    in_list = False
                result.append(f"<h1>{self._escape_html(stripped[2:])}</h1>")

            # 列表
            elif stripped.startswith(("- ", "* ", "+ ")):
                if not in_list:
                    result.append("<ul>")
                    in_list = True
                item = stripped[2:]
                result.append(f"<li>{self._escape_html(item)}</li>")

            # 空行
            elif not stripped:
                if in_list:
                    result.append("</ul>")
                    in_list = False

            # 普通段落
            else:
                if in_list:
                    result.append("</ul>")
                    in_list = False
                result.append(f"<p>{self._escape_html(stripped)}</p>")

        # 确保列表正确关闭
        if in_list:
            result.append("</ul>")

        # 处理代码块
        final_html = "\n                    ".join(result)
        final_html = final_html.replace("```", "")

        # 处理粗体和斜体
        final_html = final_html.replace("**", "<strong>").replace("**", "</strong>")
        final_html = final_html.replace("*", "<em>").replace("*", "</em>")

        return final_html

    def _escape_html(self, text: str) -> str:
        """转义 HTML 特殊字符"""
        if not text:
            return ""
        text = str(text)
        text = text.replace("&", "&amp;")
        text = text.replace("<", "&lt;")
        text = text.replace(">", "&gt;")
        text = text.replace('"', "&quot;")
        text = text.replace("'", "&#39;")
        return text

    def generate_filename(
        self, title: str, export_format: str = "html"
    ) -> str:
        """
        生成导出文件名

        Args:
            title: 演示文稿标题
            export_format: 导出格式 (html/pdf)

        Returns:
            文件名
        """
        # 清理文件名
        safe_title = title.lower()
        safe_title = safe_title.replace(" ", "_")
        safe_title = "".join(c for c in safe_title if c.isalnum() or c in "_-")
        safe_title = safe_title[:50]  # 限制长度

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{safe_title}_{timestamp}.{export_format}"


# 全局导出服务实例
export_service = ExportService()
