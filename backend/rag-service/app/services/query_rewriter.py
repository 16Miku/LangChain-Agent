# ============================================================
# Query Rewriter Service - 查询改写服务
# 基于对话历史优化检索查询，解析指代词，补充上下文
# ============================================================

import json
import re
import os
from typing import List, Dict, Any, Optional
import google.generativeai as genai

from app.config import settings


class QueryRewriterService:
    """
    查询改写服务 - 基于对话历史优化检索查询

    功能:
    - 解析指代词 (如"它"、"这个"、"刚才说的")
    - 补充隐含的上下文信息
    - 生成多个检索查询变体
    - 识别查询中的关键实体
    """

    # 查询改写提示词模板
    REWRITE_PROMPT = '''基于以下对话历史，将用户的最新问题改写为更精确的检索查询。

对话历史:
{history}

用户最新问题: {query}

要求:
1. 解析指代词 (如"它"、"这个"、"那个"、"刚才说的"、"上面提到的"、"之前的")
2. 补充隐含的上下文信息，使查询更加完整和明确
3. 生成 1-3 个检索查询变体，覆盖不同的表达方式
4. 识别查询中涉及的关键实体

输出格式 (严格 JSON):
{{
    "main_query": "主要检索查询（最精确的改写版本）",
    "variants": ["变体1", "变体2"],
    "reasoning": "改写理由（简要说明为什么这样改写）",
    "entities": ["识别出的实体1", "实体2"]
}}

注意:
- 如果原始查询已经足够清晰，main_query 可以与原始查询相同
- variants 数组可以为空，如果没有合适的变体
- entities 应该包含查询中的关键概念、技术术语、人名、产品名等
- 只输出 JSON，不要有其他内容'''

    # 多轮对话检索优化提示词
    MULTI_TURN_PROMPT = '''基于对话历史和之前的检索结果，优化当前查询以获取更相关的信息。

对话历史:
{history}

之前检索到的内容摘要:
{previous_results}

用户最新问题: {query}

要求:
1. 解析指代词，结合上下文理解用户真正想问的内容
2. 避免检索已经获取过的重复信息
3. 生成能够补充新信息的查询

输出格式 (严格 JSON):
{{
    "main_query": "优化后的主查询",
    "variants": ["变体1", "变体2"],
    "reasoning": "优化理由",
    "entities": ["关键实体"],
    "avoid_topics": ["应避免的重复主题"]
}}

只输出 JSON，不要有其他内容'''

    # 中文指代词列表
    CHINESE_PRONOUNS = [
        "它", "它们", "这", "这个", "这些", "那", "那个", "那些",
        "此", "该", "其", "之",
        "他", "她", "他们", "她们",
        "刚才", "刚刚", "上面", "上述", "前面", "之前", "前文",
        "所说的", "提到的", "说的", "讲的", "介绍的",
        "同样", "类似", "相同", "一样"
    ]

    # 英文指代词列表
    ENGLISH_PRONOUNS = [
        "it", "its", "they", "them", "their", "this", "that", "these", "those",
        "he", "she", "him", "her", "his", "hers",
        "the same", "similar", "above", "previous", "mentioned", "said"
    ]

    def __init__(self, model_name: str = "gemini-1.5-flash"):
        """
        初始化查询改写服务

        Args:
            model_name: Gemini 模型名称，默认使用 gemini-1.5-flash
        """
        self.model_name = model_name
        self._model = None
        self._initialized = False

    def _ensure_initialized(self) -> bool:
        """
        确保 Gemini API 已初始化

        Returns:
            是否初始化成功
        """
        if self._initialized:
            return True

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("[QueryRewriter] 警告: GOOGLE_API_KEY 未设置，将使用原始查询")
            return False

        try:
            genai.configure(api_key=api_key)
            self._model = genai.GenerativeModel(self.model_name)
            self._initialized = True
            return True
        except Exception as e:
            print(f"[QueryRewriter] Gemini API 初始化失败: {e}")
            return False

    async def rewrite(
        self,
        query: str,
        conversation_history: List[Dict[str, str]],
        max_history: int = 6
    ) -> Dict[str, Any]:
        """
        改写用户查询

        Args:
            query: 用户原始查询
            conversation_history: 对话历史，格式为 [{"role": "user/assistant", "content": "..."}]
            max_history: 使用的最大历史轮数

        Returns:
            {
                "main_query": "改写后的主查询",
                "variants": ["变体1", "变体2"],
                "reasoning": "改写理由",
                "entities": ["实体1", "实体2"],
                "original_query": "原始查询",
                "was_rewritten": True/False
            }
        """
        # 默认返回结果（用于 fallback）
        default_result = {
            "main_query": query,
            "variants": [],
            "reasoning": "使用原始查询",
            "entities": [],
            "original_query": query,
            "was_rewritten": False
        }

        # 检查是否需要改写
        if not self._needs_rewrite(query) and not conversation_history:
            return default_result

        # 如果没有对话历史，直接返回原始查询
        if not conversation_history:
            return default_result

        # 确保 API 已初始化
        if not self._ensure_initialized():
            return default_result

        try:
            # 格式化对话历史
            history_text = self._format_history(
                conversation_history[-max_history * 2:]  # 每轮包含 user 和 assistant
            )

            # 构建提示词
            prompt = self.REWRITE_PROMPT.format(
                history=history_text,
                query=query
            )

            # 调用 Gemini API
            response = await self._call_gemini(prompt)

            if response:
                result = self._parse_response(response)
                result["original_query"] = query
                result["was_rewritten"] = result["main_query"] != query
                return result

            return default_result

        except Exception as e:
            print(f"[QueryRewriter] 查询改写失败: {e}")
            return default_result

    async def rewrite_for_multi_turn(
        self,
        query: str,
        conversation_history: List[Dict[str, str]],
        previous_results: Optional[List[Dict[str, Any]]] = None,
        max_history: int = 6
    ) -> Dict[str, Any]:
        """
        多轮对话检索优化

        考虑之前的检索结果，避免重复检索，生成能够补充新信息的查询

        Args:
            query: 用户原始查询
            conversation_history: 对话历史
            previous_results: 之前的检索结果，格式为 [{"content": "...", "score": 0.9}]
            max_history: 使用的最大历史轮数

        Returns:
            {
                "main_query": "优化后的主查询",
                "variants": ["变体1", "变体2"],
                "reasoning": "优化理由",
                "entities": ["关键实体"],
                "avoid_topics": ["应避免的重复主题"],
                "original_query": "原始查询",
                "was_rewritten": True/False
            }
        """
        # 默认返回结果
        default_result = {
            "main_query": query,
            "variants": [],
            "reasoning": "使用原始查询",
            "entities": [],
            "avoid_topics": [],
            "original_query": query,
            "was_rewritten": False
        }

        # 如果没有对话历史和之前的结果，直接返回
        if not conversation_history and not previous_results:
            return default_result

        # 确保 API 已初始化
        if not self._ensure_initialized():
            return default_result

        try:
            # 格式化对话历史
            history_text = self._format_history(
                conversation_history[-max_history * 2:] if conversation_history else []
            )

            # 格式化之前的检索结果
            results_text = self._format_previous_results(previous_results)

            # 构建提示词
            prompt = self.MULTI_TURN_PROMPT.format(
                history=history_text or "无",
                previous_results=results_text or "无",
                query=query
            )

            # 调用 Gemini API
            response = await self._call_gemini(prompt)

            if response:
                result = self._parse_response(response)
                result["original_query"] = query
                result["was_rewritten"] = result["main_query"] != query
                # 确保 avoid_topics 字段存在
                if "avoid_topics" not in result:
                    result["avoid_topics"] = []
                return result

            return default_result

        except Exception as e:
            print(f"[QueryRewriter] 多轮查询优化失败: {e}")
            return default_result

    def _format_history(self, messages: List[Dict[str, str]]) -> str:
        """
        格式化对话历史为文本

        Args:
            messages: 消息列表，格式为 [{"role": "user/assistant", "content": "..."}]

        Returns:
            格式化后的文本
        """
        if not messages:
            return "无对话历史"

        formatted_lines = []
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")

            # 截断过长的内容
            if len(content) > 500:
                content = content[:500] + "..."

            if role == "user":
                formatted_lines.append(f"用户: {content}")
            elif role == "assistant":
                formatted_lines.append(f"助手: {content}")
            else:
                formatted_lines.append(f"{role}: {content}")

        return "\n".join(formatted_lines)

    def _format_previous_results(self, results: Optional[List[Dict[str, Any]]]) -> str:
        """
        格式化之前的检索结果

        Args:
            results: 检索结果列表

        Returns:
            格式化后的文本
        """
        if not results:
            return "无之前的检索结果"

        formatted_lines = []
        for i, result in enumerate(results[:5], 1):  # 最多显示 5 条
            content = result.get("content", "")
            # 截断过长的内容
            if len(content) > 200:
                content = content[:200] + "..."
            formatted_lines.append(f"{i}. {content}")

        return "\n".join(formatted_lines)

    def _needs_rewrite(self, query: str) -> bool:
        """
        判断查询是否需要改写

        检测是否包含指代词、省略主语等需要上下文才能理解的表达

        Args:
            query: 用户查询

        Returns:
            是否需要改写
        """
        query_lower = query.lower()

        # 检查中文指代词
        for pronoun in self.CHINESE_PRONOUNS:
            if pronoun in query:
                return True

        # 检查英文指代词
        for pronoun in self.ENGLISH_PRONOUNS:
            # 使用单词边界匹配
            pattern = r'\b' + re.escape(pronoun) + r'\b'
            if re.search(pattern, query_lower):
                return True

        # 检查是否是非常短的查询（可能省略了主语）
        if len(query) < 10 and not any(c in query for c in "？?"):
            return True

        # 检查是否以动词开头（可能省略了主语）
        verb_patterns = [
            r'^(怎么|如何|为什么|什么是|是什么|有什么|能不能|可以|应该)',
            r'^(explain|describe|what|how|why|can|could|should|is|are|does|do)\b'
        ]
        for pattern in verb_patterns:
            if re.match(pattern, query_lower):
                # 这种情况可能需要上下文，但不一定
                pass

        return False

    async def _call_gemini(self, prompt: str) -> Optional[str]:
        """
        调用 Gemini API

        Args:
            prompt: 提示词

        Returns:
            API 响应文本，失败返回 None
        """
        if not self._model:
            return None

        try:
            # 使用同步方法（Gemini SDK 的 generate_content 是同步的）
            response = self._model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,  # 较低的温度以获得更稳定的输出
                    max_output_tokens=500
                )
            )

            if response and response.text:
                return response.text.strip()

            return None

        except Exception as e:
            print(f"[QueryRewriter] Gemini API 调用失败: {e}")
            return None

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        解析 Gemini API 响应

        Args:
            response: API 响应文本

        Returns:
            解析后的字典
        """
        default_result = {
            "main_query": "",
            "variants": [],
            "reasoning": "",
            "entities": []
        }

        try:
            # 尝试提取 JSON 部分
            # 处理可能的 markdown 代码块
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response)
            if json_match:
                json_str = json_match.group(1)
            else:
                # 尝试直接解析
                json_str = response

            # 清理可能的前后空白和非 JSON 字符
            json_str = json_str.strip()

            # 找到 JSON 对象的开始和结束
            start_idx = json_str.find('{')
            end_idx = json_str.rfind('}')

            if start_idx != -1 and end_idx != -1:
                json_str = json_str[start_idx:end_idx + 1]

            result = json.loads(json_str)

            # 验证必要字段
            if "main_query" not in result or not result["main_query"]:
                return default_result

            # 确保所有字段都存在
            return {
                "main_query": result.get("main_query", ""),
                "variants": result.get("variants", []),
                "reasoning": result.get("reasoning", ""),
                "entities": result.get("entities", []),
                "avoid_topics": result.get("avoid_topics", [])
            }

        except json.JSONDecodeError as e:
            print(f"[QueryRewriter] JSON 解析失败: {e}")
            print(f"[QueryRewriter] 原始响应: {response[:200]}...")
            return default_result
        except Exception as e:
            print(f"[QueryRewriter] 响应解析失败: {e}")
            return default_result


# 单例实例
_query_rewriter_instance: Optional[QueryRewriterService] = None


def get_query_rewriter(model_name: str = "gemini-1.5-flash") -> QueryRewriterService:
    """
    获取查询改写服务单例

    Args:
        model_name: Gemini 模型名称

    Returns:
        QueryRewriterService 实例
    """
    global _query_rewriter_instance

    if _query_rewriter_instance is None:
        _query_rewriter_instance = QueryRewriterService(model_name)

    return _query_rewriter_instance
