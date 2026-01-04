# ============================================================
# Presentation Service - AI Assistant Tests
# AI 助手功能自动化测试
# ============================================================

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.services.intent_parser import IntentParserService, get_intent_parser
from app.schemas import ParsedIntent, ChatMessage


class TestIntentParserService:
    """意图解析服务测试"""

    @pytest.fixture
    def intent_parser(self):
        """创建意图解析器实例"""
        with patch.object(IntentParserService, '_get_llm') as mock_llm:
            # Mock LLM
            mock_llm.return_value = MagicMock()
            parser = IntentParserService()
            return parser

    def test_parse_json_response_valid(self, intent_parser):
        """测试有效 JSON 解析"""
        content = '{"intent_type": "edit_title", "target_slide": 2, "new_value": "新标题", "response_message": "已修改", "confidence": 0.9}'
        result = intent_parser._parse_json_response(content)

        assert result["intent_type"] == "edit_title"
        assert result["target_slide"] == 2
        assert result["new_value"] == "新标题"

    def test_parse_json_response_with_markdown(self, intent_parser):
        """测试带 markdown 标记的 JSON 解析"""
        content = """```json
{"intent_type": "insert_slide", "position": 3, "response_message": "已插入", "confidence": 0.8}
```"""
        result = intent_parser._parse_json_response(content)

        assert result["intent_type"] == "insert_slide"
        assert result["position"] == 3

    def test_parse_json_response_invalid(self, intent_parser):
        """测试无效 JSON 处理"""
        content = "这不是有效的 JSON"
        result = intent_parser._parse_json_response(content)

        assert result["intent_type"] == "chat"
        assert "confidence" in result

    def test_validate_and_fix_intent_valid(self, intent_parser):
        """测试有效意图验证"""
        intent_data = {
            "intent_type": "edit_title",
            "target_slide": 2,
            "new_value": "新标题",
            "response_message": "已修改",
            "confidence": 0.9,
        }
        result = intent_parser._validate_and_fix_intent(
            intent_data,
            slide_count=5,
            current_slide=1,
        )

        assert isinstance(result, ParsedIntent)
        assert result.intent_type == "edit_title"
        assert result.target_slide == 2
        assert result.new_value == "新标题"

    def test_validate_and_fix_intent_invalid_slide_index(self, intent_parser):
        """测试无效幻灯片索引修正"""
        intent_data = {
            "intent_type": "edit_title",
            "target_slide": 10,  # 超出范围
            "new_value": "新标题",
            "response_message": "已修改",
            "confidence": 0.9,
        }
        result = intent_parser._validate_and_fix_intent(
            intent_data,
            slide_count=5,
            current_slide=1,
        )

        # 应该被修正为最后一张幻灯片
        assert result.target_slide == 4

    def test_validate_and_fix_intent_negative_slide_index(self, intent_parser):
        """测试负数幻灯片索引修正"""
        intent_data = {
            "intent_type": "edit_title",
            "target_slide": -1,
            "new_value": "新标题",
            "response_message": "已修改",
            "confidence": 0.9,
        }
        result = intent_parser._validate_and_fix_intent(
            intent_data,
            slide_count=5,
            current_slide=1,
        )

        # 应该被修正为第一张幻灯片
        assert result.target_slide == 0

    def test_validate_and_fix_intent_default_slide(self, intent_parser):
        """测试默认使用当前幻灯片"""
        intent_data = {
            "intent_type": "edit_title",
            "target_slide": None,
            "new_value": "新标题",
            "response_message": "已修改",
            "confidence": 0.9,
        }
        result = intent_parser._validate_and_fix_intent(
            intent_data,
            slide_count=5,
            current_slide=2,
        )

        # 应该使用当前幻灯片索引
        assert result.target_slide == 2

    def test_validate_and_fix_intent_invalid_type(self, intent_parser):
        """测试无效意图类型修正"""
        intent_data = {
            "intent_type": "invalid_type",
            "response_message": "未知操作",
            "confidence": 0.5,
        }
        result = intent_parser._validate_and_fix_intent(
            intent_data,
            slide_count=5,
            current_slide=1,
        )

        # 应该被修正为 chat
        assert result.intent_type == "chat"

    def test_validate_and_fix_intent_theme_fuzzy_match(self, intent_parser):
        """测试主题模糊匹配"""
        intent_data = {
            "intent_type": "change_theme",
            "theme": "深色",  # 应该匹配到 night
            "response_message": "已更换主题",
            "confidence": 0.8,
        }
        result = intent_parser._validate_and_fix_intent(
            intent_data,
            slide_count=5,
            current_slide=1,
        )

        # 模糊匹配可能失败，theme 可能为 None
        # 但不应该崩溃
        assert result.intent_type == "change_theme"

    def test_validate_and_fix_intent_layout_validation(self, intent_parser):
        """测试布局类型验证"""
        intent_data = {
            "intent_type": "change_layout",
            "target_slide": 1,
            "layout": "bullet_points",  # 有效布局
            "response_message": "已更改布局",
            "confidence": 0.9,
        }
        result = intent_parser._validate_and_fix_intent(
            intent_data,
            slide_count=5,
            current_slide=1,
        )

        assert result.layout == "bullet_points"

    def test_validate_and_fix_intent_invalid_layout(self, intent_parser):
        """测试无效布局类型处理"""
        intent_data = {
            "intent_type": "change_layout",
            "target_slide": 1,
            "layout": "invalid_layout",  # 无效布局
            "response_message": "已更改布局",
            "confidence": 0.9,
        }
        result = intent_parser._validate_and_fix_intent(
            intent_data,
            slide_count=5,
            current_slide=1,
        )

        # 无效布局应该被设为 None
        assert result.layout is None


class TestIntentParserServiceAsync:
    """意图解析服务异步测试"""

    def test_parse_intent_with_mock_llm(self):
        """测试使用 Mock LLM 解析意图"""
        with patch.object(IntentParserService, '_get_llm') as mock_get_llm:
            # 创建 Mock LLM
            mock_llm = AsyncMock()
            mock_llm.ainvoke.return_value = MagicMock(
                content='{"intent_type": "edit_title", "target_slide": 0, "new_value": "测试标题", "response_message": "已修改标题", "confidence": 0.95}'
            )
            mock_get_llm.return_value = mock_llm

            parser = IntentParserService()

            # 运行异步函数
            result = asyncio.get_event_loop().run_until_complete(
                parser.parse_intent(
                    message="把第1页的标题改成测试标题",
                    slide_count=5,
                    current_slide=0,
                    slide_titles=["标题1", "标题2", "标题3", "标题4", "标题5"],
                )
            )

            assert result.intent_type == "edit_title"
            assert result.target_slide == 0
            assert result.new_value == "测试标题"

    def test_parse_intent_llm_error_handling(self):
        """测试 LLM 错误处理"""
        with patch.object(IntentParserService, '_get_llm') as mock_get_llm:
            # 创建会抛出异常的 Mock LLM
            mock_llm = AsyncMock()
            mock_llm.ainvoke.side_effect = Exception("LLM Error")
            mock_get_llm.return_value = mock_llm

            parser = IntentParserService()

            # 运行异步函数
            result = asyncio.get_event_loop().run_until_complete(
                parser.parse_intent(
                    message="测试消息",
                    slide_count=5,
                    current_slide=0,
                    slide_titles=["标题1", "标题2", "标题3", "标题4", "标题5"],
                )
            )

            # 应该返回默认的 chat 意图
            assert result.intent_type == "chat"
            assert result.confidence == 0.0


class TestGetIntentParser:
    """测试单例获取"""

    def test_get_intent_parser_singleton(self):
        """测试单例模式"""
        # 重置单例
        import app.services.intent_parser as parser_module
        parser_module._intent_parser = None

        with patch.object(IntentParserService, '_get_llm'):
            parser1 = get_intent_parser()
            parser2 = get_intent_parser()

            assert parser1 is parser2
