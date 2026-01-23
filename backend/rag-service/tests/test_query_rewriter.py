# ============================================================
# QueryRewriterService 自动化测试
# ============================================================
# 运行方式: cd backend/rag-service && python -m pytest tests/test_query_rewriter.py -v
# ============================================================

import pytest
import asyncio
import sys
import os
from unittest.mock import Mock, patch, AsyncMock

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.query_rewriter import QueryRewriterService, get_query_rewriter


class TestQueryRewriterService:
    """QueryRewriterService 单元测试"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """每个测试前初始化"""
        self.service = QueryRewriterService()
        yield

    # ============================================================
    # 指代词检测测试
    # ============================================================

    def test_needs_rewrite_chinese_pronouns(self):
        """测试中文指代词检测"""
        # 包含指代词的查询应该需要改写
        queries_need_rewrite = [
            "它的实现原理是什么？",
            "这个怎么使用？",
            "那个方法有什么优点？",
            "刚才说的技术叫什么？",
            "上面提到的框架",
            "之前的问题",
            "他们是怎么做的？",
        ]

        for query in queries_need_rewrite:
            assert self.service._needs_rewrite(query) is True, f"应该需要改写: {query}"
            print(f"  [PASS] 检测到需要改写: {query}")

    def test_needs_rewrite_english_pronouns(self):
        """测试英文指代词检测"""
        queries_need_rewrite = [
            "What is it used for?",
            "How does this work?",
            "Can you explain that?",
            "What are their advantages?",
            "The same approach",
        ]

        for query in queries_need_rewrite:
            assert self.service._needs_rewrite(query) is True, f"应该需要改写: {query}"
            print(f"  [PASS] 检测到需要改写: {query}")

    def test_needs_rewrite_clear_queries(self):
        """测试清晰查询不需要改写"""
        # 清晰的查询不应该需要改写（没有指代词）
        clear_queries = [
            "RAG 检索增强生成是什么？",
            "Python 如何实现多线程？",
            "LangChain 框架的核心组件有哪些？",
            "What is machine learning?",
            "How to implement a REST API in FastAPI?",
        ]

        for query in clear_queries:
            result = self.service._needs_rewrite(query)
            print(f"  查询: {query} -> 需要改写: {result}")

    def test_needs_rewrite_short_queries(self):
        """测试短查询检测"""
        # 非常短的查询可能需要上下文
        short_queries = [
            "原理",
            "用法",
            "例子",
        ]

        for query in short_queries:
            result = self.service._needs_rewrite(query)
            assert result is True, f"短查询应该需要改写: {query}"
            print(f"  [PASS] 短查询需要改写: {query}")

    # ============================================================
    # 对话历史格式化测试
    # ============================================================

    def test_format_history_empty(self):
        """测试空对话历史格式化"""
        result = self.service._format_history([])
        assert result == "无对话历史"
        print(f"  [PASS] 空历史: {result}")

    def test_format_history_single_turn(self):
        """测试单轮对话格式化"""
        history = [
            {"role": "user", "content": "RAG 是什么？"},
            {"role": "assistant", "content": "RAG 是检索增强生成..."}
        ]

        result = self.service._format_history(history)

        assert "用户: RAG 是什么？" in result
        assert "助手: RAG 是检索增强生成..." in result
        print(f"  [PASS] 单轮对话格式化正确")

    def test_format_history_multi_turn(self):
        """测试多轮对话格式化"""
        history = [
            {"role": "user", "content": "什么是向量数据库？"},
            {"role": "assistant", "content": "向量数据库是专门存储向量的数据库..."},
            {"role": "user", "content": "有哪些常用的？"},
            {"role": "assistant", "content": "常用的有 Milvus、Pinecone、Weaviate..."},
        ]

        result = self.service._format_history(history)

        assert result.count("用户:") == 2
        assert result.count("助手:") == 2
        print(f"  [PASS] 多轮对话格式化正确")

    def test_format_history_truncate_long_content(self):
        """测试长内容截断"""
        long_content = "A" * 1000
        history = [
            {"role": "user", "content": long_content}
        ]

        result = self.service._format_history(history)

        # 应该被截断到 500 字符 + "..."
        assert len(result) < len(long_content)
        assert "..." in result
        print(f"  [PASS] 长内容被正确截断")

    # ============================================================
    # 之前检索结果格式化测试
    # ============================================================

    def test_format_previous_results_empty(self):
        """测试空检索结果格式化"""
        result = self.service._format_previous_results(None)
        assert result == "无之前的检索结果"

        result = self.service._format_previous_results([])
        assert result == "无之前的检索结果"
        print(f"  [PASS] 空检索结果格式化正确")

    def test_format_previous_results_normal(self):
        """测试正常检索结果格式化"""
        results = [
            {"content": "RAG 是一种结合检索和生成的技术", "score": 0.95},
            {"content": "向量数据库用于存储嵌入向量", "score": 0.88},
        ]

        result = self.service._format_previous_results(results)

        assert "1." in result
        assert "2." in result
        assert "RAG" in result
        print(f"  [PASS] 检索结果格式化正确")

    def test_format_previous_results_max_five(self):
        """测试最多显示 5 条结果"""
        results = [
            {"content": f"结果 {i}", "score": 0.9 - i * 0.1}
            for i in range(10)
        ]

        result = self.service._format_previous_results(results)

        # 应该只有 5 条
        assert "5." in result
        assert "6." not in result
        print(f"  [PASS] 最多显示 5 条结果")

    # ============================================================
    # JSON 响应解析测试
    # ============================================================

    def test_parse_response_valid_json(self):
        """测试有效 JSON 解析"""
        response = '''
        {
            "main_query": "RAG 检索增强生成的实现原理",
            "variants": ["RAG 工作原理", "检索增强生成技术原理"],
            "reasoning": "将指代词'它'替换为上文提到的 RAG",
            "entities": ["RAG", "检索增强生成"]
        }
        '''

        result = self.service._parse_response(response)

        assert result["main_query"] == "RAG 检索增强生成的实现原理"
        assert len(result["variants"]) == 2
        assert "RAG" in result["entities"]
        print(f"  [PASS] 有效 JSON 解析正确")

    def test_parse_response_markdown_code_block(self):
        """测试 Markdown 代码块中的 JSON"""
        response = '''
        这是改写结果：
        ```json
        {
            "main_query": "Python 多线程实现方法",
            "variants": [],
            "reasoning": "查询已经足够清晰",
            "entities": ["Python", "多线程"]
        }
        ```
        '''

        result = self.service._parse_response(response)

        assert result["main_query"] == "Python 多线程实现方法"
        print(f"  [PASS] Markdown 代码块 JSON 解析正确")

    def test_parse_response_invalid_json(self):
        """测试无效 JSON 处理"""
        response = "这不是有效的 JSON 格式"

        result = self.service._parse_response(response)

        # 应该返回默认结果
        assert result["main_query"] == ""
        assert result["variants"] == []
        print(f"  [PASS] 无效 JSON 返回默认结果")

    def test_parse_response_missing_main_query(self):
        """测试缺少 main_query 字段"""
        response = '''
        {
            "variants": ["变体1"],
            "reasoning": "测试"
        }
        '''

        result = self.service._parse_response(response)

        # 缺少 main_query 应该返回默认结果
        assert result["main_query"] == ""
        print(f"  [PASS] 缺少 main_query 返回默认结果")

    # ============================================================
    # 查询改写测试 (Mock API)
    # ============================================================

    @pytest.mark.asyncio
    async def test_rewrite_without_history(self):
        """测试无对话历史时的改写"""
        query = "RAG 是什么？"

        result = await self.service.rewrite(query, [])

        # 无历史时应该返回原始查询
        assert result["main_query"] == query
        assert result["was_rewritten"] is False
        print(f"  [PASS] 无历史时返回原始查询")

    @pytest.mark.asyncio
    async def test_rewrite_without_api_key(self):
        """测试无 API Key 时的 fallback"""
        # 确保没有 API Key
        with patch.dict(os.environ, {"GOOGLE_API_KEY": ""}, clear=False):
            service = QueryRewriterService()
            service._initialized = False  # 重置初始化状态

            history = [
                {"role": "user", "content": "RAG 是什么？"},
                {"role": "assistant", "content": "RAG 是检索增强生成..."}
            ]
            query = "它的原理是什么？"

            result = await service.rewrite(query, history)

            # 应该 fallback 到原始查询
            assert result["main_query"] == query
            assert result["was_rewritten"] is False
            print(f"  [PASS] 无 API Key 时 fallback 正确")

    @pytest.mark.asyncio
    async def test_rewrite_with_mock_api(self):
        """测试使用 Mock API 的改写"""
        service = QueryRewriterService()

        # Mock Gemini API 响应
        mock_response = Mock()
        mock_response.text = '''
        {
            "main_query": "RAG 检索增强生成的实现原理是什么",
            "variants": ["RAG 工作机制", "检索增强生成原理"],
            "reasoning": "将'它'替换为上文的 RAG",
            "entities": ["RAG", "检索增强生成"]
        }
        '''

        with patch.object(service, '_call_gemini', return_value=mock_response.text):
            service._initialized = True

            history = [
                {"role": "user", "content": "RAG 是什么？"},
                {"role": "assistant", "content": "RAG 是检索增强生成..."}
            ]
            query = "它的实现原理是什么？"

            result = await service.rewrite(query, history)

            assert result["main_query"] == "RAG 检索增强生成的实现原理是什么"
            assert result["was_rewritten"] is True
            assert "RAG" in result["entities"]
            print(f"  [PASS] Mock API 改写正确")

    @pytest.mark.asyncio
    async def test_rewrite_api_failure_fallback(self):
        """测试 API 调用失败时的 fallback"""
        service = QueryRewriterService()
        service._initialized = True

        # Mock API 调用失败
        with patch.object(service, '_call_gemini', return_value=None):
            history = [
                {"role": "user", "content": "什么是 LangChain？"},
                {"role": "assistant", "content": "LangChain 是一个框架..."}
            ]
            query = "它有什么特点？"

            result = await service.rewrite(query, history)

            # API 失败应该 fallback 到原始查询
            assert result["main_query"] == query
            assert result["was_rewritten"] is False
            print(f"  [PASS] API 失败时 fallback 正确")

    # ============================================================
    # 多轮对话改写测试
    # ============================================================

    @pytest.mark.asyncio
    async def test_multi_turn_rewrite_with_mock(self):
        """测试多轮对话改写"""
        service = QueryRewriterService()

        mock_response = '''
        {
            "main_query": "向量数据库的性能优化方法",
            "variants": ["Milvus 性能调优"],
            "reasoning": "基于之前讨论的向量数据库主题",
            "entities": ["向量数据库", "性能优化"],
            "avoid_topics": ["向量数据库基本概念"]
        }
        '''

        with patch.object(service, '_call_gemini', return_value=mock_response):
            service._initialized = True

            history = [
                {"role": "user", "content": "什么是向量数据库？"},
                {"role": "assistant", "content": "向量数据库是..."},
            ]
            previous_results = [
                {"content": "向量数据库的基本概念...", "score": 0.9}
            ]
            query = "怎么优化性能？"

            result = await service.rewrite_for_multi_turn(
                query, history, previous_results
            )

            assert result["main_query"] == "向量数据库的性能优化方法"
            assert "avoid_topics" in result
            print(f"  [PASS] 多轮对话改写正确")


class TestGetQueryRewriter:
    """测试 get_query_rewriter 工厂函数"""

    def test_returns_singleton(self):
        """测试返回单例"""
        service1 = get_query_rewriter()
        service2 = get_query_rewriter()

        assert service1 is service2
        assert isinstance(service1, QueryRewriterService)
        print(f"  [PASS] get_query_rewriter 返回单例")

    def test_default_model(self):
        """测试默认模型"""
        service = get_query_rewriter()
        assert service.model_name == "gemini-1.5-flash"
        print(f"  [PASS] 默认模型为 gemini-1.5-flash")


class TestQueryRewriterIntegration:
    """集成测试 - 需要真实 API Key"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """检查是否有 API Key"""
        self.has_api_key = bool(os.getenv("GOOGLE_API_KEY"))
        if not self.has_api_key:
            pytest.skip("跳过集成测试: GOOGLE_API_KEY 未设置")
        self.service = QueryRewriterService()
        yield

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_real_rewrite_chinese(self):
        """测试真实 API 中文改写"""
        history = [
            {"role": "user", "content": "RAG 是什么？"},
            {"role": "assistant", "content": "RAG（Retrieval-Augmented Generation）是检索增强生成技术，它结合了信息检索和文本生成，先从知识库中检索相关文档，再基于检索结果生成回答。"}
        ]
        query = "它的实现原理是什么？"

        result = await self.service.rewrite(query, history)

        print(f"\n  原始查询: {query}")
        print(f"  改写后: {result['main_query']}")
        print(f"  变体: {result['variants']}")
        print(f"  理由: {result['reasoning']}")
        print(f"  实体: {result['entities']}")

        # 改写后的查询应该包含 RAG 相关内容
        assert "RAG" in result["main_query"] or "检索" in result["main_query"]

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_real_rewrite_english(self):
        """测试真实 API 英文改写"""
        history = [
            {"role": "user", "content": "What is LangChain?"},
            {"role": "assistant", "content": "LangChain is a framework for developing applications powered by language models."}
        ]
        query = "How does it work?"

        result = await self.service.rewrite(query, history)

        print(f"\n  Original: {query}")
        print(f"  Rewritten: {result['main_query']}")
        print(f"  Variants: {result['variants']}")

        # 改写后应该包含 LangChain
        assert "LangChain" in result["main_query"] or "langchain" in result["main_query"].lower()


if __name__ == "__main__":
    # 直接运行测试
    pytest.main([__file__, "-v", "--tb=short", "-m", "not integration"])
