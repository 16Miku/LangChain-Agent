# ============================================================
# Chat Service - Context Compressor
# 对话上下文压缩服务 - 智能压缩对话历史以节省 Token
# ============================================================

import asyncio
import json
import re
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class CompressionStrategy(Enum):
    """压缩策略枚举"""
    TRUNCATE = "truncate"  # 简单截断
    SUMMARIZE = "summarize"  # LLM 摘要
    SLIDING_WINDOW = "sliding_window"  # 滑动窗口
    IMPORTANCE_BASED = "importance_based"  # 基于重要性


@dataclass
class CompressionResult:
    """压缩结果数据结构"""
    messages: List[Dict[str, Any]]
    original_tokens: int
    compressed_tokens: int
    compression_ratio: float
    strategy_used: CompressionStrategy
    summary: Optional[str] = None


class ContextCompressor:
    """
    对话上下文压缩服务

    功能:
    1. 估算对话历史的 Token 数量
    2. 智能压缩对话历史，保留关键信息
    3. 支持多种压缩策略
    4. 生成对话摘要

    使用示例:
    ```python
    from langchain_google_genai import ChatGoogleGenerativeAI

    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    compressor = ContextCompressor(llm, max_tokens=4000)

    messages = [
        {"role": "user", "content": "你好"},
        {"role": "assistant", "content": "你好！有什么可以帮助你的？"},
        # ... 更多消息
    ]

    compressed = await compressor.compress(messages)
    ```
    """

    # Token 估算常量 (基于 GPT 分词器的经验值)
    CHARS_PER_TOKEN_EN = 4  # 英文平均每 4 个字符一个 token
    CHARS_PER_TOKEN_ZH = 1.5  # 中文平均每 1.5 个字符一个 token

    # 重要性关键词
    IMPORTANCE_KEYWORDS = {
        "high": [
            "重要", "关键", "必须", "请记住", "注意",
            "important", "critical", "must", "remember", "note",
            "结论", "总结", "决定", "确认",
            "conclusion", "summary", "decision", "confirm",
        ],
        "medium": [
            "因为", "所以", "但是", "然而", "如果",
            "because", "therefore", "but", "however", "if",
            "建议", "推荐", "可以", "应该",
            "suggest", "recommend", "can", "should",
        ],
    }

    # 摘要提示词模板
    SUMMARY_PROMPT = """请将以下对话历史压缩成一个简洁的摘要，保留关键信息和上下文。

对话历史:
{conversation}

要求:
1. 保留用户的主要问题和需求
2. 保留 AI 的关键回答和结论
3. 保留重要的数据、数字和事实
4. 使用简洁的语言
5. 摘要长度控制在 {max_length} 字以内

摘要:"""

    def __init__(
        self,
        llm: Any = None,
        max_tokens: int = 4000,
        target_ratio: float = 0.5,
        preserve_recent: int = 3,
        strategy: CompressionStrategy = CompressionStrategy.IMPORTANCE_BASED,
    ):
        """
        初始化上下文压缩器

        Args:
            llm: LangChain LLM 实例，用于生成摘要
            max_tokens: 最大允许的 Token 数量
            target_ratio: 目标压缩比例 (0-1)
            preserve_recent: 保留最近的消息数量
            strategy: 默认压缩策略
        """
        self.llm = llm
        self.max_tokens = max_tokens
        self.target_ratio = target_ratio
        self.preserve_recent = preserve_recent
        self.strategy = strategy

    def _count_tokens(self, text: str) -> int:
        """
        估算文本的 Token 数量

        使用简单的字符计数方法估算，
        区分中英文以提高准确性

        Args:
            text: 输入文本

        Returns:
            估算的 Token 数量
        """
        if not text:
            return 0

        # 分离中文和非中文字符
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
        non_chinese = re.sub(r'[\u4e00-\u9fff]', '', text)

        # 分别计算
        chinese_tokens = len(chinese_chars) / self.CHARS_PER_TOKEN_ZH
        english_tokens = len(non_chinese) / self.CHARS_PER_TOKEN_EN

        return int(chinese_tokens + english_tokens)

    def _count_messages_tokens(self, messages: List[Dict[str, Any]]) -> int:
        """
        估算消息列表的总 Token 数量

        Args:
            messages: 消息列表

        Returns:
            总 Token 数量
        """
        total = 0
        for msg in messages:
            content = msg.get("content", "")
            if isinstance(content, str):
                total += self._count_tokens(content)
            elif isinstance(content, list):
                # 多模态消息
                for part in content:
                    if isinstance(part, dict) and "text" in part:
                        total += self._count_tokens(part["text"])
            # 角色标记的开销
            total += 4  # 每条消息的固定开销
        return total

    def _calculate_importance(self, message: Dict[str, Any]) -> float:
        """
        计算消息的重要性分数

        Args:
            message: 消息

        Returns:
            重要性分数 (0-1)
        """
        content = message.get("content", "")
        if isinstance(content, list):
            content = " ".join(
                p.get("text", "") for p in content if isinstance(p, dict)
            )

        content_lower = content.lower()
        score = 0.5  # 基础分数

        # 检查高重要性关键词
        for keyword in self.IMPORTANCE_KEYWORDS["high"]:
            if keyword.lower() in content_lower:
                score += 0.15

        # 检查中等重要性关键词
        for keyword in self.IMPORTANCE_KEYWORDS["medium"]:
            if keyword.lower() in content_lower:
                score += 0.05

        # 包含代码的消息更重要
        if "```" in content or "def " in content or "class " in content:
            score += 0.1

        # 包含数字/数据的消息更重要
        if re.search(r'\d+\.?\d*', content):
            score += 0.05

        # 较长的消息可能包含更多信息
        if len(content) > 500:
            score += 0.1

        # 用户消息通常更重要(包含需求)
        if message.get("role") == "user":
            score += 0.1

        return min(score, 1.0)

    async def _summarize(
        self,
        messages: List[Dict[str, Any]],
        max_length: int = 500,
    ) -> str:
        """
        使用 LLM 生成对话摘要

        Args:
            messages: 消息列表
            max_length: 摘要最大长度

        Returns:
            对话摘要
        """
        if not self.llm:
            # 无 LLM 时使用简单摘要
            return self._simple_summarize(messages, max_length)

        # 构建对话文本
        conversation_text = ""
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            if isinstance(content, list):
                content = " ".join(
                    p.get("text", "") for p in content if isinstance(p, dict)
                )
            conversation_text += f"{role}: {content}\n\n"

        # 构建提示词
        prompt = self.SUMMARY_PROMPT.format(
            conversation=conversation_text,
            max_length=max_length,
        )

        try:
            # 调用 LLM 生成摘要
            response = await self.llm.ainvoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.warning(f"LLM 摘要生成失败: {e}，使用简单摘要")
            return self._simple_summarize(messages, max_length)

    def _simple_summarize(
        self,
        messages: List[Dict[str, Any]],
        max_length: int = 500,
    ) -> str:
        """
        简单摘要方法(无 LLM 时使用)

        Args:
            messages: 消息列表
            max_length: 最大长度

        Returns:
            简单摘要
        """
        summary_parts = []

        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            if isinstance(content, list):
                content = " ".join(
                    p.get("text", "") for p in content if isinstance(p, dict)
                )

            # 截取每条消息的前 100 个字符
            truncated = content[:100] + "..." if len(content) > 100 else content
            summary_parts.append(f"[{role}] {truncated}")

        summary = "\n".join(summary_parts)
        if len(summary) > max_length:
            summary = summary[:max_length] + "..."

        return summary

    def _truncate_messages(
        self,
        messages: List[Dict[str, Any]],
        target_tokens: int,
    ) -> List[Dict[str, Any]]:
        """
        截断消息列表

        Args:
            messages: 消息列表
            target_tokens: 目标 Token 数量

        Returns:
            截断后的消息列表
        """
        if not messages:
            return []

        # 保留最近的消息
        preserved = messages[-self.preserve_recent:] if len(messages) > self.preserve_recent else messages
        preserved_tokens = self._count_messages_tokens(preserved)

        if preserved_tokens >= target_tokens:
            # 即使保留的消息也超过限制，需要截断内容
            return self._truncate_content(preserved, target_tokens)

        # 从前面的消息中选择
        remaining_tokens = target_tokens - preserved_tokens
        older_messages = messages[:-self.preserve_recent] if len(messages) > self.preserve_recent else []

        selected = []
        current_tokens = 0

        for msg in reversed(older_messages):
            msg_tokens = self._count_messages_tokens([msg])
            if current_tokens + msg_tokens <= remaining_tokens:
                selected.insert(0, msg)
                current_tokens += msg_tokens
            else:
                break

        return selected + list(preserved)

    def _truncate_content(
        self,
        messages: List[Dict[str, Any]],
        target_tokens: int,
    ) -> List[Dict[str, Any]]:
        """
        截断消息内容

        Args:
            messages: 消息列表
            target_tokens: 目标 Token 数量

        Returns:
            内容截断后的消息列表
        """
        result = []
        tokens_per_message = target_tokens // len(messages) if messages else 0

        for msg in messages:
            content = msg.get("content", "")
            if isinstance(content, str):
                max_chars = tokens_per_message * self.CHARS_PER_TOKEN_EN
                if len(content) > max_chars:
                    content = content[:int(max_chars)] + "..."
            result.append({**msg, "content": content})

        return result

    def _sliding_window(
        self,
        messages: List[Dict[str, Any]],
        target_tokens: int,
    ) -> List[Dict[str, Any]]:
        """
        滑动窗口压缩

        保留最近的消息，丢弃较早的消息

        Args:
            messages: 消息列表
            target_tokens: 目标 Token 数量

        Returns:
            压缩后的消息列表
        """
        if not messages:
            return []

        result = []
        current_tokens = 0

        # 从最新的消息开始
        for msg in reversed(messages):
            msg_tokens = self._count_messages_tokens([msg])
            if current_tokens + msg_tokens <= target_tokens:
                result.insert(0, msg)
                current_tokens += msg_tokens
            else:
                break

        return result

    def _importance_based_compress(
        self,
        messages: List[Dict[str, Any]],
        target_tokens: int,
    ) -> List[Dict[str, Any]]:
        """
        基于重要性的压缩

        保留重要性高的消息和最近的消息

        Args:
            messages: 消息列表
            target_tokens: 目标 Token 数量

        Returns:
            压缩后的消息列表
        """
        if not messages:
            return []

        # 计算每条消息的重要性
        scored_messages = [
            (msg, self._calculate_importance(msg), i)
            for i, msg in enumerate(messages)
        ]

        # 保留最近的消息
        recent_indices = set(range(max(0, len(messages) - self.preserve_recent), len(messages)))

        # 按重要性排序(保留原始索引)
        sorted_messages = sorted(
            scored_messages,
            key=lambda x: (x[2] in recent_indices, x[1]),  # 最近的优先，然后按重要性
            reverse=True,
        )

        # 选择消息直到达到 Token 限制
        selected_indices = set()
        current_tokens = 0

        for msg, score, idx in sorted_messages:
            msg_tokens = self._count_messages_tokens([msg])
            if current_tokens + msg_tokens <= target_tokens:
                selected_indices.add(idx)
                current_tokens += msg_tokens

        # 按原始顺序返回
        return [
            messages[i] for i in sorted(selected_indices)
        ]

    async def compress(
        self,
        messages: List[Dict[str, Any]],
        strategy: Optional[CompressionStrategy] = None,
    ) -> CompressionResult:
        """
        压缩对话历史，保留关键信息

        Args:
            messages: 对话消息列表
            strategy: 压缩策略(可选，默认使用初始化时的策略)

        Returns:
            CompressionResult 对象
        """
        if not messages:
            return CompressionResult(
                messages=[],
                original_tokens=0,
                compressed_tokens=0,
                compression_ratio=1.0,
                strategy_used=strategy or self.strategy,
            )

        strategy = strategy or self.strategy
        original_tokens = self._count_messages_tokens(messages)

        # 如果不需要压缩
        if original_tokens <= self.max_tokens:
            return CompressionResult(
                messages=messages,
                original_tokens=original_tokens,
                compressed_tokens=original_tokens,
                compression_ratio=1.0,
                strategy_used=strategy,
            )

        # 计算目标 Token 数
        target_tokens = int(self.max_tokens * self.target_ratio)

        # 根据策略压缩
        summary = None

        if strategy == CompressionStrategy.TRUNCATE:
            compressed = self._truncate_messages(messages, target_tokens)

        elif strategy == CompressionStrategy.SLIDING_WINDOW:
            compressed = self._sliding_window(messages, target_tokens)

        elif strategy == CompressionStrategy.SUMMARIZE:
            # 生成摘要并保留最近消息
            older_messages = messages[:-self.preserve_recent] if len(messages) > self.preserve_recent else []
            recent_messages = messages[-self.preserve_recent:] if len(messages) > self.preserve_recent else messages

            if older_messages:
                summary = await self._summarize(older_messages)
                summary_message = {
                    "role": "system",
                    "content": f"[对话历史摘要]\n{summary}",
                }
                compressed = [summary_message] + list(recent_messages)
            else:
                compressed = list(recent_messages)

        elif strategy == CompressionStrategy.IMPORTANCE_BASED:
            compressed = self._importance_based_compress(messages, target_tokens)

        else:
            compressed = self._truncate_messages(messages, target_tokens)

        compressed_tokens = self._count_messages_tokens(compressed)

        return CompressionResult(
            messages=compressed,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=compressed_tokens / original_tokens if original_tokens > 0 else 1.0,
            strategy_used=strategy,
            summary=summary,
        )

    async def compress_if_needed(
        self,
        messages: List[Dict[str, Any]],
        threshold_ratio: float = 0.8,
    ) -> List[Dict[str, Any]]:
        """
        仅在需要时压缩消息

        Args:
            messages: 消息列表
            threshold_ratio: 触发压缩的阈值比例

        Returns:
            压缩后的消息列表(或原始列表)
        """
        current_tokens = self._count_messages_tokens(messages)
        threshold = int(self.max_tokens * threshold_ratio)

        if current_tokens <= threshold:
            return messages

        result = await self.compress(messages)
        return result.messages

    def estimate_remaining_capacity(
        self,
        messages: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        估算剩余容量

        Args:
            messages: 当前消息列表

        Returns:
            容量信息字典
        """
        current_tokens = self._count_messages_tokens(messages)
        remaining = self.max_tokens - current_tokens

        return {
            "current_tokens": current_tokens,
            "max_tokens": self.max_tokens,
            "remaining_tokens": max(0, remaining),
            "usage_ratio": current_tokens / self.max_tokens if self.max_tokens > 0 else 0,
            "needs_compression": current_tokens > self.max_tokens * 0.8,
        }


# 便捷函数
async def compress_context(
    messages: List[Dict[str, Any]],
    max_tokens: int = 4000,
    llm: Any = None,
) -> List[Dict[str, Any]]:
    """
    便捷函数: 压缩对话上下文

    Args:
        messages: 消息列表
        max_tokens: 最大 Token 数
        llm: LLM 实例(可选)

    Returns:
        压缩后的消息列表
    """
    compressor = ContextCompressor(llm=llm, max_tokens=max_tokens)
    result = await compressor.compress(messages)
    return result.messages
