# ============================================================
# Presentation Service - Presentation Service
# 演示文稿业务逻辑服务
# ============================================================

import json
import uuid
from typing import List, Optional
from datetime import datetime

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import settings


class PresentationService:
    """演示文稿服务"""

    def __init__(self, db):
        self.db = db

    def _get_llm(self, temperature: float = 0.7):
        """
        根据配置获取 LLM 实例
        支持 Google Gemini 和 OpenAI 兼容模式
        """
        if settings.LLM_PROVIDER == "openai_compatible":
            if not settings.OPENAI_BASE_URL or not settings.OPENAI_API_KEY:
                raise ValueError("OpenAI compatible mode requires OPENAI_BASE_URL and OPENAI_API_KEY")

            return ChatOpenAI(
                model=settings.OPENAI_MODEL,
                base_url=settings.OPENAI_BASE_URL,
                api_key=settings.OPENAI_API_KEY,
                temperature=temperature,
                timeout=120,
                max_retries=2,
            )
        else:
            # Google Gemini 模式
            if not settings.GOOGLE_API_KEY:
                raise ValueError("Google mode requires GOOGLE_API_KEY")

            return ChatGoogleGenerativeAI(
                model=settings.GOOGLE_MODEL,
                google_api_key=settings.GOOGLE_API_KEY,
                temperature=temperature,
            )

    async def generate_presentation(
        self,
        user_id: str,  # 接受字符串类型的 user_id
        topic: str,
        slide_count: int = 10,
        target_audience: str = "general",
        presentation_type: str = "informative",
        theme: str = "modern_business",
        include_images: bool = True,
        image_style: str = "professional",
        language: str = "zh-CN",
        custom_title: Optional[str] = None,
    ):
        """
        AI 生成演示文稿
        """
        from app.models import Presentation

        # 调用 AI 生成幻灯片内容
        slides_data = await self._generate_slides_with_ai(
            topic=topic,
            slide_count=slide_count,
            target_audience=target_audience,
            presentation_type=presentation_type,
            language=language,
        )

        # 创建演示文稿记录
        presentation = Presentation(
            user_id=user_id,  # 已经是字符串类型
            title=custom_title or topic,
            description=f"关于 {topic} 的演示文稿",
            slides=slides_data,
            theme=theme,
            target_audience=target_audience,
            presentation_type=presentation_type,
            include_images=include_images,
            image_style=image_style,
            slide_count=len(slides_data),
            status="completed",
        )

        self.db.add(presentation)
        await self.db.flush()  # 只 flush 不 commit，让 get_db 统一管理事务
        await self.db.refresh(presentation)

        print(f"[Service] Generated presentation ID: {presentation.id}")
        print(f"[Service] User ID: {presentation.user_id}")

        return presentation

    async def _generate_slides_with_ai(
        self,
        topic: str,
        slide_count: int,
        target_audience: str,
        presentation_type: str,
        language: str,
    ) -> List[dict]:
        """
        使用 AI 生成幻灯片内容
        """
        # 构建 System Prompt
        system_prompt = self._build_generation_system_prompt(
            target_audience=target_audience,
            presentation_type=presentation_type,
            language=language,
        )

        # 构建 User Prompt
        user_prompt = self._build_generation_user_prompt(
            topic=topic,
            slide_count=slide_count,
        )

        # 调用 LLM
        llm = self._get_llm()

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]

        response = await llm.ainvoke(messages)
        content = response.content

        # 解析 AI 返回的 JSON
        slides = self._parse_ai_response(content)

        return slides

    def _build_generation_system_prompt(
        self,
        target_audience: str,
        presentation_type: str,
        language: str,
    ) -> str:
        """构建生成演示文稿的系统提示词"""
        lang_map = {
            "zh-CN": "中文",
            "en-US": "英文",
        }
        lang = lang_map.get(language, "中文")

        return f"""你是一个专业的演示文稿内容生成助手。

## 任务
根据用户提供的主题，生成一个结构化的演示文稿大纲。

## 要求
1. 幻灯片数量：按用户要求
2. 目标受众：{target_audience}
3. 演示类型：{presentation_type}
4. 语言：{lang}

## 输出格式
必须返回有效的 JSON 数组，每个元素包含：
- title: 幻灯片标题
- content: 内容（使用 Markdown 列表格式，用 \\n 分行）
- layout: 布局类型（可选，默认 bullet_points）
  可选值：title_cover, title_section, bullet_points, two_column, image_text, quote_center, thank_you
- notes: 演讲者备注（可选）

## 布局类型说明
- title_cover: 封面页（第一张）
- title_section: 章节页（新章节开始）
- bullet_points: 列表页（默认）
- two_column: 双栏布局
- image_text: 图文混排
- quote_center: 引用页
- thank_you: 结尾页（最后一张）

## 示例
[
  {{"title": "欢迎", "content": "- 感谢参加\\n- 今天我们将讨论...", "layout": "title_cover"}},
  {{"title": "议程", "content": "- 介绍\\n- 核心内容\\n- 总结", "layout": "bullet_points"}},
  {{"title": "总结", "content": "- 要点回顾\\n- Q&A", "layout": "thank_you"}}
]

## 注意
- 第一张应该是封面页（title_cover）
- 中间页使用 bullet_points 或其他内容布局
- 最后一张应该是结尾页（thank_you）
- 内容要简洁有力，适合演讲展示
- 必须确保输出是纯有效的 JSON，不要包含任何其他文字"""

    def _build_generation_user_prompt(
        self,
        topic: str,
        slide_count: int,
    ) -> str:
        """构建用户提示词"""
        return f"""请为以下主题生成一个 {slide_count} 张幻灯片的演示文稿大纲：

主题：{topic}

请直接返回 JSON 数组，不要包含任何其他说明文字。"""

    def _parse_ai_response(self, content: str) -> List[dict]:
        """解析 AI 返回的内容为幻灯片数组"""
        # 尝试直接解析 JSON
        try:
            # 去除可能的 markdown 代码块标记
            content = content.strip()
            if content.startswith("```"):
                # 找到第一个换行
                lines = content.split("\n")
                if len(lines) > 1:
                    # 去掉第一行 ```json 或 ```
                    content = "\n".join(lines[1:])
                # 去掉最后一行 ```
                if content.endswith("```"):
                    content = content[:-3].rstrip()

            # 尝试解析 JSON
            slides = json.loads(content)

            if isinstance(slides, list):
                return slides
            elif isinstance(slides, dict) and "slides" in slides:
                return slides["slides"]
            else:
                raise ValueError("Invalid response format")

        except json.JSONDecodeError:
            # 如果直接解析失败，尝试提取 JSON
            import re
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                try:
                    slides = json.loads(json_match.group())
                    if isinstance(slides, list):
                        return slides
                except:
                    pass

        # 如果都失败了，返回默认结构
        return self._get_default_slides()

    def _get_default_slides(self) -> List[dict]:
        """获取默认幻灯片结构"""
        return [
            {
                "title": "演示文稿",
                "content": "- 欢迎参加本次演示",
                "layout": "title_cover"
            },
            {
                "title": "主要内容",
                "content": "- 要点一\\n- 要点二\\n- 要点三",
                "layout": "bullet_points"
            },
            {
                "title": "谢谢观看",
                "content": "- Q&A",
                "layout": "thank_you"
            }
        ]

    async def regenerate_slide(
        self,
        presentation,
        slide_index: int,
        feedback: str,
    ) -> "Presentation":
        """
        重新生成指定幻灯片
        """
        # 获取当前演示文稿上下文
        topic = presentation.title
        current_slide = presentation.slides[slide_index]

        # 构建 Prompt
        system_prompt = f"""你是一个专业的演示文稿编辑助手。

## 任务
根据用户的反馈，重新生成一张幻灯片的内容。

## 上下文
- 演示文稿主题：{topic}
- 当前幻灯片标题：{current_slide.get('title', '未知')}

## 输出格式
返回单个幻灯片对象的 JSON：
{{
  "title": "幻灯片标题",
  "content": "内容（使用 Markdown 列表格式，用 \\\\n 分行）",
  "layout": "布局类型（可选）"
}}

## 注意
- 内容要简洁有力，适合演讲展示
- 保持与演示文稿主题的一致性
- 根据用户反馈进行调整"""

        user_prompt = f"""用户反馈：{feedback}

请重新生成这张幻灯片的内容。直接返回 JSON，不要包含其他说明文字。"""

        # 调用 LLM
        llm = self._get_llm()

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]

        response = await llm.ainvoke(messages)
        content = response.content

        # 解析返回的幻灯片
        new_slide = self._parse_slide_response(content)

        # 更新幻灯片
        slides = presentation.slides.copy()
        slides[slide_index] = new_slide
        presentation.slides = slides

        return presentation

    def _parse_slide_response(self, content: str) -> dict:
        """解析单个幻灯片响应"""
        try:
            content = content.strip()
            if content.startswith("```"):
                lines = content.split("\n")
                if len(lines) > 1:
                    content = "\n".join(lines[1:])
                if content.endswith("```"):
                    content = content[:-3].rstrip()

            slide = json.loads(content)
            if isinstance(slide, dict):
                return slide
        except:
            pass

        # 默认幻灯片
        return {
            "title": "重新生成的内容",
            "content": "- 要点一\\n- 要点二",
            "layout": "bullet_points"
        }
