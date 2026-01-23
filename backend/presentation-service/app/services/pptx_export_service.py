# ============================================================
# Presentation Service - PPTX Export Service
# 原生 PPTX 导出服务 (使用 python-pptx)
# ============================================================

import io
import re
import requests
from typing import Dict, Any, List, Optional, Tuple
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

from app.services.layout_engine import LayoutType


class PptxExportService:
    """
    原生 PPTX 导出服务
    使用 python-pptx 库生成真正的 PowerPoint 文件
    """

    # 幻灯片尺寸 (16:9)
    SLIDE_WIDTH = Inches(13.333)
    SLIDE_HEIGHT = Inches(7.5)
    MARGIN = Inches(0.5)
    CONTENT_WIDTH = Inches(12.333)

    # 主题配色
    THEME_COLORS = {
        "modern_business": {"background": "FFFFFF", "title": "1E3A8A", "text": "1E293B", "accent": "3B82F6", "subtitle": "64748B"},
        "corporate_blue": {"background": "FFFFFF", "title": "1E40AF", "text": "1F2937", "accent": "2563EB", "subtitle": "6B7280"},
        "elegant_dark": {"background": "1A1A1A", "title": "D4AF37", "text": "F4E4BC", "accent": "D4AF37", "subtitle": "A0A0A0"},
        "dark_tech": {"background": "0A0A0A", "title": "00FF88", "text": "E0E0E0", "accent": "00D4FF", "subtitle": "888888"},
        "gradient_purple": {"background": "1A1A2E", "title": "E94560", "text": "EAEAEA", "accent": "E94560", "subtitle": "A0A0A0"},
        "neon_future": {"background": "0D0D0D", "title": "FF00FF", "text": "FFFFFF", "accent": "00FFFF", "subtitle": "888888"},
        "minimal_white": {"background": "FFFFFF", "title": "111111", "text": "333333", "accent": "666666", "subtitle": "888888"},
        "nature_green": {"background": "F0FDF4", "title": "166534", "text": "1F2937", "accent": "22C55E", "subtitle": "6B7280"},
        "soft_pastel": {"background": "FDF2F8", "title": "BE185D", "text": "4A4A4A", "accent": "EC4899", "subtitle": "9CA3AF"},
        "creative_colorful": {"background": "FFFFFF", "title": "7C3AED", "text": "1F2937", "accent": "F59E0B", "subtitle": "6B7280"},
        "warm_sunset": {"background": "FFFBEB", "title": "C2410C", "text": "1F2937", "accent": "F97316", "subtitle": "78716C"},
        "academic_classic": {"background": "FFFEF5", "title": "1E3A5F", "text": "2C3E50", "accent": "8B4513", "subtitle": "7F8C8D"},
        "anime_dark": {"background": "1A1A2E", "title": "FF6B9D", "text": "E0E0E0", "accent": "C084FC", "subtitle": "A78BFA"},
        "anime_cute": {"background": "FFF0F5", "title": "FF69B4", "text": "4A4A4A", "accent": "FFB6C1", "subtitle": "DDA0DD"},
        "cyberpunk": {"background": "0D0221", "title": "FF00FF", "text": "E0E0E0", "accent": "00FFFF", "subtitle": "FF6EC7"},
        "eva_nerv": {"background": "1C1C1C", "title": "5B2C6F", "text": "E0E0E0", "accent": "1ABC9C", "subtitle": "E74C3C"},
        "retro_pixel": {"background": "2D1B69", "title": "FF6B6B", "text": "F8F8F8", "accent": "4ECDC4", "subtitle": "FFE66D"},
    }

    def _hex_to_rgb(self, hex_color: str) -> RGBColor:
        """十六进制转 RGBColor"""
        hex_color = hex_color.lstrip('#')
        return RGBColor(int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16))

    def _get_theme_colors(self, theme: str) -> Dict[str, str]:
        """获取主题配色"""
        return self.THEME_COLORS.get(theme, self.THEME_COLORS["modern_business"])

    def _parse_content(self, content: str) -> List[Tuple[str, int, bool]]:
        """解析内容为 (文本, 级别, 是否列表项)"""
        if not content:
            return []
        content = content.replace("\\n", "\n")
        lines = []
        for line in content.split("\n"):
            stripped = line.strip()
            if not stripped:
                continue
            level = min(2, (len(line) - len(line.lstrip())) // 2)
            is_bullet = stripped.startswith(("- ", "* ", "+ ")) or bool(re.match(r'^\d+\.\s', stripped))
            text = re.sub(r'^[-*+]\s|^\d+\.\s|^#{1,3}\s', '', stripped)
            lines.append((text, level, is_bullet))
        return lines

    def _add_title_slide(self, prs: Presentation, title: str, subtitle: str, colors: Dict[str, str]) -> None:
        """封面页"""
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = self._hex_to_rgb(colors["background"])

        # 标题
        title_box = slide.shapes.add_textbox(self.MARGIN, Inches(2.5), self.CONTENT_WIDTH, Inches(1.5))
        p = title_box.text_frame.paragraphs[0]
        p.text = title
        p.font.size = Pt(44)
        p.font.bold = True
        p.font.color.rgb = self._hex_to_rgb(colors["title"])
        p.alignment = PP_ALIGN.CENTER

        # 装饰线
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(5.5), Inches(4), Inches(2.333), Pt(4))
        line.fill.solid()
        line.fill.fore_color.rgb = self._hex_to_rgb(colors["accent"])
        line.line.fill.background()

        # 副标题
        if subtitle:
            sub_box = slide.shapes.add_textbox(self.MARGIN, Inches(4.2), self.CONTENT_WIDTH, Inches(1))
            p = sub_box.text_frame.paragraphs[0]
            p.text = subtitle
            p.font.size = Pt(24)
            p.font.color.rgb = self._hex_to_rgb(colors["subtitle"])
            p.alignment = PP_ALIGN.CENTER

    def _add_section_slide(self, prs: Presentation, title: str, colors: Dict[str, str]) -> None:
        """章节页"""
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = self._hex_to_rgb(colors["background"])

        title_box = slide.shapes.add_textbox(self.MARGIN, Inches(3), self.CONTENT_WIDTH, Inches(1.5))
        p = title_box.text_frame.paragraphs[0]
        p.text = title
        p.font.size = Pt(40)
        p.font.bold = True
        p.font.color.rgb = self._hex_to_rgb(colors["title"])
        p.alignment = PP_ALIGN.CENTER

        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(5.5), Inches(4.5), Inches(2.333), Pt(4))
        line.fill.solid()
        line.fill.fore_color.rgb = self._hex_to_rgb(colors["accent"])
        line.line.fill.background()

    def _add_content_slide(self, prs: Presentation, title: str, content: str, colors: Dict[str, str], notes: str = "") -> None:
        """内容页"""
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = self._hex_to_rgb(colors["background"])

        # 标题
        title_box = slide.shapes.add_textbox(self.MARGIN, self.MARGIN, self.CONTENT_WIDTH, Inches(0.8))
        p = title_box.text_frame.paragraphs[0]
        p.text = title
        p.font.size = Pt(32)
        p.font.bold = True
        p.font.color.rgb = self._hex_to_rgb(colors["title"])

        # 装饰线
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, self.MARGIN, Inches(1.3), Inches(1.5), Pt(3))
        line.fill.solid()
        line.fill.fore_color.rgb = self._hex_to_rgb(colors["accent"])
        line.line.fill.background()

        # 内容
        content_box = slide.shapes.add_textbox(self.MARGIN, Inches(1.6), self.CONTENT_WIDTH, Inches(5.4))
        tf = content_box.text_frame
        tf.word_wrap = True
        lines = self._parse_content(content)

        if lines:
            text, level, is_bullet = lines[0]
            p = tf.paragraphs[0]
            p.text = text
            p.font.size = Pt(20)
            p.font.color.rgb = self._hex_to_rgb(colors["text"])
            p.level = level
            if is_bullet:
                p.bullet = True

            for text, level, is_bullet in lines[1:]:
                p = tf.add_paragraph()
                p.text = text
                p.font.size = Pt(20 - level * 2)
                p.font.color.rgb = self._hex_to_rgb(colors["text"])
                p.level = level
                if is_bullet:
                    p.bullet = True
                p.space_before = Pt(8)

        if notes:
            slide.notes_slide.notes_text_frame.text = notes

    def _add_two_column_slide(self, prs: Presentation, title: str, content: str, colors: Dict[str, str], notes: str = "") -> None:
        """双栏页"""
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = self._hex_to_rgb(colors["background"])

        # 标题
        title_box = slide.shapes.add_textbox(self.MARGIN, self.MARGIN, self.CONTENT_WIDTH, Inches(0.8))
        p = title_box.text_frame.paragraphs[0]
        p.text = title
        p.font.size = Pt(32)
        p.font.bold = True
        p.font.color.rgb = self._hex_to_rgb(colors["title"])

        # 分割内容
        lines = self._parse_content(content)
        mid = len(lines) // 2
        left_lines, right_lines = lines[:mid] if mid else lines, lines[mid:] if mid else []

        # 左栏
        left_box = slide.shapes.add_textbox(self.MARGIN, Inches(1.5), Inches(5.9), Inches(5.5))
        tf = left_box.text_frame
        tf.word_wrap = True
        if left_lines:
            p = tf.paragraphs[0]
            p.text = left_lines[0][0]
            p.font.size = Pt(18)
            p.font.color.rgb = self._hex_to_rgb(colors["text"])
            if left_lines[0][2]:
                p.bullet = True
            for text, _, is_bullet in left_lines[1:]:
                p = tf.add_paragraph()
                p.text = text
                p.font.size = Pt(18)
                p.font.color.rgb = self._hex_to_rgb(colors["text"])
                if is_bullet:
                    p.bullet = True

        # 右栏
        right_box = slide.shapes.add_textbox(Inches(6.9), Inches(1.5), Inches(5.9), Inches(5.5))
        tf = right_box.text_frame
        tf.word_wrap = True
        if right_lines:
            p = tf.paragraphs[0]
            p.text = right_lines[0][0]
            p.font.size = Pt(18)
            p.font.color.rgb = self._hex_to_rgb(colors["text"])
            if right_lines[0][2]:
                p.bullet = True
            for text, _, is_bullet in right_lines[1:]:
                p = tf.add_paragraph()
                p.text = text
                p.font.size = Pt(18)
                p.font.color.rgb = self._hex_to_rgb(colors["text"])
                if is_bullet:
                    p.bullet = True

        if notes:
            slide.notes_slide.notes_text_frame.text = notes

    def _add_quote_slide(self, prs: Presentation, title: str, content: str, colors: Dict[str, str], notes: str = "") -> None:
        """引用页"""
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = self._hex_to_rgb(colors["background"])

        # 引号
        quote_box = slide.shapes.add_textbox(Inches(1), Inches(2), Inches(1), Inches(1))
        p = quote_box.text_frame.paragraphs[0]
        p.text = "\u201C"
        p.font.size = Pt(72)
        p.font.color.rgb = self._hex_to_rgb(colors["accent"])

        # 内容
        content_box = slide.shapes.add_textbox(Inches(2), Inches(2.5), Inches(9.333), Inches(3))
        p = content_box.text_frame.paragraphs[0]
        p.text = content.replace("\\n", "\n").strip()
        p.font.size = Pt(28)
        p.font.italic = True
        p.font.color.rgb = self._hex_to_rgb(colors["text"])
        p.alignment = PP_ALIGN.CENTER

        if title:
            source_box = slide.shapes.add_textbox(Inches(2), Inches(5.5), Inches(9.333), Inches(0.5))
            p = source_box.text_frame.paragraphs[0]
            p.text = f"— {title}"
            p.font.size = Pt(18)
            p.font.color.rgb = self._hex_to_rgb(colors["subtitle"])
            p.alignment = PP_ALIGN.CENTER

        if notes:
            slide.notes_slide.notes_text_frame.text = notes

    def _add_thank_you_slide(self, prs: Presentation, title: str, content: str, colors: Dict[str, str]) -> None:
        """感谢页"""
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = self._hex_to_rgb(colors["background"])

        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(5.5), Inches(2.8), Inches(2.333), Pt(4))
        line.fill.solid()
        line.fill.fore_color.rgb = self._hex_to_rgb(colors["accent"])
        line.line.fill.background()

        title_box = slide.shapes.add_textbox(self.MARGIN, Inches(3), self.CONTENT_WIDTH, Inches(1.5))
        p = title_box.text_frame.paragraphs[0]
        p.text = title or "Thank You"
        p.font.size = Pt(48)
        p.font.bold = True
        p.font.color.rgb = self._hex_to_rgb(colors["title"])
        p.alignment = PP_ALIGN.CENTER

        if content:
            sub_box = slide.shapes.add_textbox(self.MARGIN, Inches(4.8), self.CONTENT_WIDTH, Inches(1))
            p = sub_box.text_frame.paragraphs[0]
            p.text = content.replace("\\n", " ").strip()
            p.font.size = Pt(20)
            p.font.color.rgb = self._hex_to_rgb(colors["subtitle"])
            p.alignment = PP_ALIGN.CENTER

    def _create_slide(self, prs: Presentation, slide_data: Dict[str, Any], colors: Dict[str, str]) -> None:
        """根据布局创建幻灯片"""
        layout = slide_data.get("layout", "bullet_points")
        title = slide_data.get("title", "")
        content = slide_data.get("content", "")
        notes = slide_data.get("notes", "")

        if layout == LayoutType.TITLE_COVER.value:
            self._add_title_slide(prs, title, content, colors)
        elif layout == LayoutType.TITLE_SECTION.value:
            self._add_section_slide(prs, title, colors)
        elif layout == LayoutType.QUOTE_CENTER.value:
            self._add_quote_slide(prs, title, content, colors, notes)
        elif layout == LayoutType.THANK_YOU.value:
            self._add_thank_you_slide(prs, title, content, colors)
        elif layout in (LayoutType.TWO_COLUMN.value, LayoutType.THREE_COLUMN.value, LayoutType.COMPARISON.value):
            self._add_two_column_slide(prs, title, content, colors, notes)
        else:
            self._add_content_slide(prs, title, content, colors, notes)

    async def export_to_pptx(self, presentation_data: Dict[str, Any], theme: str = "modern_business") -> bytes:
        """导出为 PPTX"""
        prs = Presentation()
        prs.slide_width = self.SLIDE_WIDTH
        prs.slide_height = self.SLIDE_HEIGHT
        colors = self._get_theme_colors(theme)

        for slide_data in presentation_data.get("slides", []):
            self._create_slide(prs, slide_data, colors)

        output = io.BytesIO()
        prs.save(output)
        output.seek(0)
        return output.getvalue()

    def generate_filename(self, title: str) -> str:
        """生成文件名"""
        from datetime import datetime
        safe_title = "".join(c for c in title.lower().replace(" ", "_") if c.isalnum() or c in "_-")[:50]
        return f"{safe_title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pptx"


# 全局实例
pptx_export_service = PptxExportService()
