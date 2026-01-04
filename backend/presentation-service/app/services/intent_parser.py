# ============================================================
# Presentation Service - Intent Parser Service
# 自然语言指令解析服务
# ============================================================

import json
import re
from typing import Optional, List, Dict, Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import settings
from app.schemas import ParsedIntent, ChatMessage


class IntentParserService:
    """
    自然语言意图解析服务
    将用户的自然语言指令解析为结构化的操作意图
    """

    # 支持的布局类型
    LAYOUT_TYPES = [
        "title_cover",      # 封面页
        "title_section",    # 章节页
        "bullet_points",    # 列表页
        "two_column",       # 双栏布局
        "image_text",       # 图文混排
        "quote_center",     # 引用页
        "thank_you",        # 结尾页
    ]

    # 支持的主题
    THEMES = [
        "black", "white", "league", "beige", "sky",
        "night", "serif", "simple", "solarized",
        "modern_business", "dark_tech", "creative_colorful",
        "minimal_academic", "elegant_dark",
    ]

    def __init__(self):
        self.llm = self._get_llm()

    def _get_llm(self, temperature: float = 0.3):
        """
        获取 LLM 实例
        使用较低的 temperature 以获得更稳定的解析结果
        """
        if settings.LLM_PROVIDER == "openai_compatible":
            if not settings.OPENAI_BASE_URL or not settings.OPENAI_API_KEY:
                raise ValueError("OpenAI compatible mode requires OPENAI_BASE_URL and OPENAI_API_KEY")

            return ChatOpenAI(
                model=settings.OPENAI_MODEL,
                base_url=settings.OPENAI_BASE_URL,
                api_key=settings.OPENAI_API_KEY,
                temperature=temperature,
                timeout=60,
                max_retries=2,
            )
        else:
            if not settings.GOOGLE_API_KEY:
                raise ValueError("Google mode requires GOOGLE_API_KEY")

            return ChatGoogleGenerativeAI(
                model=settings.GOOGLE_MODEL,
                google_api_key=settings.GOOGLE_API_KEY,
                temperature=temperature,
            )

    def _build_system_prompt(
        self,
        slide_count: int,
        current_slide: int,
        slide_titles: List[str],
    ) -> str:
        """构建系统提示词"""
        # 构建幻灯片列表描述
        slides_desc = "\n".join([
            f"  - 第{i+1}页: {title}"
            for i, title in enumerate(slide_titles)
        ])

        return f"""你是一个 PPT 编辑助手，负责解析用户的自然语言指令并转换为结构化操作。

## 当前演示文稿信息
- 幻灯片总数: {slide_count}
- 当前选中: 第{current_slide + 1}页
- 幻灯片列表:
{slides_desc}

## 支持的操作类型
1. edit_title - 修改幻灯片标题
2. edit_content - 修改幻灯片内容
3. edit_notes - 修改演讲者备注
4. insert_slide - 插入新幻灯片
5. delete_slide - 删除幻灯片
6. change_layout - 更改布局类型
7. change_theme - 更换整体主题
8. regenerate - 重新生成幻灯片内容
9. reorder_slides - 调整幻灯片顺序
10. chat - 普通对话（不执行操作）

## 支持的布局类型
{', '.join(self.LAYOUT_TYPES)}

## 支持的主题
{', '.join(self.THEMES)}

## 输出格式
必须返回有效的 JSON 对象：
{{
  "intent_type": "操作类型",
  "target_slide": 目标幻灯片索引(从0开始，可为null),
  "new_value": "新值(标题/内容等，可为null)",
  "layout": "布局类型(可为null)",
  "theme": "主题名称(可为null)",
  "position": 插入位置(可为null),
  "response_message": "给用户的友好回复",
  "confidence": 0.95,
  "requires_confirmation": false
}}

## 解析规则
1. "第N页" 或 "第N张" 表示幻灯片索引为 N-1
2. "当前页" 表示 target_slide = {current_slide}
3. "最后一页" 表示 target_slide = {slide_count - 1}
4. 如果用户没有指定页码，默认使用当前页
5. 删除操作需要 requires_confirmation = true
6. 如果无法理解用户意图，使用 intent_type = "chat"

## 示例
用户: "把第3页的标题改成人工智能发展史"
输出: {{"intent_type": "edit_title", "target_slide": 2, "new_value": "人工智能发展史", "response_message": "好的，我已将第3页的标题修改为「人工智能发展史」", "confidence": 0.95, "requires_confirmation": false}}

用户: "在当前页后面插入一张新幻灯片"
输出: {{"intent_type": "insert_slide", "target_slide": null, "position": {current_slide + 1}, "response_message": "好的，我已在当前页后插入了一张新幻灯片", "confidence": 0.9, "requires_confirmation": false}}

用户: "删除第5页"
输出: {{"intent_type": "delete_slide", "target_slide": 4, "response_message": "确定要删除第5页吗？此操作不可撤销。", "confidence": 0.95, "requires_confirmation": true}}

用户: "把整个PPT换成深色主题"
输出: {{"intent_type": "change_theme", "theme": "night", "response_message": "好的，我已将主题更换为深色主题", "confidence": 0.9, "requires_confirmation": false}}

用户: "你好"
输出: {{"intent_type": "chat", "response_message": "你好！我是 PPT 编辑助手，可以帮你修改标题、内容、布局，或者插入/删除幻灯片。请告诉我你想做什么？", "confidence": 1.0, "requires_confirmation": false}}

## 注意
- 必须确保输出是纯有效的 JSON，不要包含任何其他文字
- response_message 要友好、简洁
- 对于模糊的指令，可以在 response_message 中询问用户"""

    async def parse_intent(
        self,
        message: str,
        slide_count: int,
        current_slide: int,
        slide_titles: List[str],
        conversation_history: List[ChatMessage] = None,
    ) -> ParsedIntent:
        """
        解析用户意图

        Args:
            message: 用户消息
            slide_count: 幻灯片总数
            current_slide: 当前选中的幻灯片索引
            slide_titles: 所有幻灯片的标题列表
            conversation_history: 对话历史

        Returns:
            ParsedIntent: 解析后的意图
        """
        # 构建系统提示词
        system_prompt = self._build_system_prompt(
            slide_count=slide_count,
            current_slide=current_slide,
            slide_titles=slide_titles,
        )

        # 构建消息列表
        messages = [SystemMessage(content=system_prompt)]

        # 添加对话历史（最近 5 条）
        if conversation_history:
            for msg in conversation_history[-5:]:
                if msg.role == "user":
                    messages.append(HumanMessage(content=msg.content))
                elif msg.role == "assistant":
                    messages.append(SystemMessage(content=f"[助手之前的回复]: {msg.content}"))

        # 添加当前用户消息
        messages.append(HumanMessage(content=f"用户指令: {message}\n\n请解析并返回 JSON。"))

        try:
            # 调用 LLM
            response = await self.llm.ainvoke(messages)
            content = response.content

            # 解析 JSON
            intent_data = self._parse_json_response(content)

            # 验证和修正意图
            intent = self._validate_and_fix_intent(
                intent_data,
                slide_count=slide_count,
                current_slide=current_slide,
            )

            return intent

        except Exception as e:
            # 解析失败，返回默认的 chat 意图
            return ParsedIntent(
                intent_type="chat",
                response_message=f"抱歉，我没有理解你的意思。你可以尝试说：\n- \"把第N页的标题改成xxx\"\n- \"在当前页后插入一张新幻灯片\"\n- \"删除第N页\"\n- \"把布局改成双栏\"",
                confidence=0.0,
                requires_confirmation=False,
            )

    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """解析 LLM 返回的 JSON"""
        content = content.strip()

        # 去除 markdown 代码块标记
        if content.startswith("```"):
            lines = content.split("\n")
            if len(lines) > 1:
                content = "\n".join(lines[1:])
            if content.endswith("```"):
                content = content[:-3].rstrip()

        # 尝试直接解析
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # 尝试提取 JSON 对象
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        # 返回默认值
        return {
            "intent_type": "chat",
            "response_message": "抱歉，我没有理解你的意思。",
            "confidence": 0.0,
        }

    def _validate_and_fix_intent(
        self,
        intent_data: Dict[str, Any],
        slide_count: int,
        current_slide: int,
    ) -> ParsedIntent:
        """验证并修正意图数据"""
        intent_type = intent_data.get("intent_type", "chat")

        # 验证 intent_type
        valid_types = [
            "edit_title", "edit_content", "edit_notes",
            "insert_slide", "delete_slide", "change_layout",
            "change_theme", "regenerate", "reorder_slides",
            "chat", "unknown"
        ]
        if intent_type not in valid_types:
            intent_type = "chat"

        # 验证 target_slide
        target_slide = intent_data.get("target_slide")
        if target_slide is not None:
            if not isinstance(target_slide, int):
                try:
                    target_slide = int(target_slide)
                except (ValueError, TypeError):
                    target_slide = current_slide

            # 确保在有效范围内
            if target_slide < 0:
                target_slide = 0
            elif target_slide >= slide_count:
                target_slide = slide_count - 1

        # 对于需要目标幻灯片的操作，默认使用当前页
        if intent_type in ["edit_title", "edit_content", "edit_notes", "change_layout", "regenerate"]:
            if target_slide is None:
                target_slide = current_slide

        # 验证 layout
        layout = intent_data.get("layout")
        if layout and layout not in self.LAYOUT_TYPES:
            layout = None

        # 验证 theme
        theme = intent_data.get("theme")
        if theme and theme not in self.THEMES:
            # 尝试模糊匹配
            theme_lower = theme.lower()
            for t in self.THEMES:
                if theme_lower in t.lower() or t.lower() in theme_lower:
                    theme = t
                    break
            else:
                theme = None

        # 验证 position
        position = intent_data.get("position")
        if position is not None:
            if not isinstance(position, int):
                try:
                    position = int(position)
                except (ValueError, TypeError):
                    position = None

            if position is not None:
                if position < 0:
                    position = 0
                elif position > slide_count:
                    position = slide_count

        # 验证 confidence
        confidence = intent_data.get("confidence", 0.5)
        if not isinstance(confidence, (int, float)):
            confidence = 0.5
        confidence = max(0.0, min(1.0, float(confidence)))

        # 构建 ParsedIntent
        return ParsedIntent(
            intent_type=intent_type,
            target_slide=target_slide,
            new_value=intent_data.get("new_value"),
            layout=layout,
            theme=theme,
            position=position,
            response_message=intent_data.get("response_message", "操作已完成"),
            confidence=confidence,
            requires_confirmation=intent_data.get("requires_confirmation", False),
        )


# 单例实例
_intent_parser: Optional[IntentParserService] = None


def get_intent_parser() -> IntentParserService:
    """获取意图解析服务单例"""
    global _intent_parser
    if _intent_parser is None:
        _intent_parser = IntentParserService()
    return _intent_parser
