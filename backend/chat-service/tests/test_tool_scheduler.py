# ============================================================
# Chat Service - Tool Scheduler Tests
# 工具调度器、上下文压缩器、工具缓存的单元测试
# ============================================================

import asyncio
import pytest
import time
from typing import Dict, Any

# 导入被测试的模块
from app.services.tool_scheduler import (
    ToolScheduler,
    ToolCall,
    ToolStatus,
    ExecutionPlan,
    execute_tools_parallel,
)
from app.services.context_compressor import (
    ContextCompressor,
    CompressionStrategy,
    CompressionResult,
    compress_context,
)
from app.services.tool_cache import (
    ToolCache,
    CacheEntry,
    CacheStats,
    get_tool_cache,
    clear_global_cache,
)


# ============================================================
# ToolScheduler 测试
# ============================================================

class TestToolScheduler:
    """工具调度器测试类"""

    def setup_method(self):
        """每个测试方法前的设置"""
        self.scheduler = ToolScheduler(max_parallel=3, timeout=10.0)

    def test_analyze_empty_dependencies(self):
        """测试空工具列表的依赖分析"""
        result = self.scheduler.analyze_dependencies([])

        assert result["parallel_groups"] == []
        assert result["dependencies"] == {}
        assert result["execution_order"] == []
        assert result["total_tools"] == 0

    def test_analyze_independent_tools(self):
        """测试独立工具的依赖分析"""
        tool_calls = [
            {"id": "1", "name": "search_engine", "args": {"query": "AI"}},
            {"id": "2", "name": "search_engine", "args": {"query": "ML"}},
            {"id": "3", "name": "scrape_as_markdown", "args": {"url": "https://example.com"}},
        ]

        result = self.scheduler.analyze_dependencies(tool_calls)

        assert result["total_tools"] == 3
        # 独立工具应该可以并行执行
        assert len(result["parallel_groups"]) >= 1
        # 第一组应该包含所有独立工具
        assert len(result["parallel_groups"][0]) == 3

    def test_analyze_explicit_dependencies(self):
        """测试显式依赖(参数引用)的分析"""
        tool_calls = [
            {"id": "search1", "name": "search_engine", "args": {"query": "AI"}},
            {"id": "process1", "name": "summarize", "args": {"text": "$search1.result"}},
        ]

        result = self.scheduler.analyze_dependencies(tool_calls)

        assert result["total_tools"] == 2
        assert "process1" in result["dependencies"]
        assert "search1" in result["dependencies"]["process1"]
        # 应该有两个执行组
        assert len(result["parallel_groups"]) == 2

    def test_analyze_multiple_dependencies(self):
        """测试多重依赖的分析"""
        tool_calls = [
            {"id": "a", "name": "search_engine", "args": {"query": "topic1"}},
            {"id": "b", "name": "search_engine", "args": {"query": "topic2"}},
            {"id": "c", "name": "summarize", "args": {"text": "$a.result and $b.result"}},
        ]

        result = self.scheduler.analyze_dependencies(tool_calls)

        assert result["total_tools"] == 3
        assert "c" in result["dependencies"]
        assert set(result["dependencies"]["c"]) == {"a", "b"}

    def test_create_execution_plan(self):
        """测试执行计划创建"""
        tool_calls = [
            {"id": "1", "name": "search_engine", "args": {"query": "test"}},
            {"id": "2", "name": "rag_search", "args": {"query": "test"}},
        ]

        plan = self.scheduler.create_execution_plan(tool_calls)

        assert isinstance(plan, ExecutionPlan)
        assert plan.total_tools == 2
        assert len(plan.execution_order) == 2

    @pytest.mark.asyncio
    async def test_execute_parallel_simple(self):
        """测试简单并行执行"""
        tool_calls = [
            {"id": "1", "name": "test_tool", "args": {"value": 1}},
            {"id": "2", "name": "test_tool", "args": {"value": 2}},
        ]

        execution_order = []

        async def mock_executor(name: str, args: dict) -> str:
            execution_order.append(args["value"])
            await asyncio.sleep(0.1)
            return f"result_{args['value']}"

        results = await self.scheduler.execute_parallel(tool_calls, mock_executor)

        assert len(results) == 2
        assert results[0] == "result_1"
        assert results[1] == "result_2"

    @pytest.mark.asyncio
    async def test_execute_parallel_with_dependencies(self):
        """测试带依赖的并行执行"""
        tool_calls = [
            {"id": "first", "name": "search", "args": {"query": "test"}},
            {"id": "second", "name": "process", "args": {"data": "$first.result"}},
        ]

        call_times = {}

        async def mock_executor(name: str, args: dict) -> str:
            call_times[name] = time.time()
            await asyncio.sleep(0.1)
            if name == "search":
                return "search_result"
            return f"processed: {args.get('data', '')}"

        results = await self.scheduler.execute_parallel(tool_calls, mock_executor)

        assert len(results) == 2
        # 第二个工具应该在第一个之后执行
        assert call_times["process"] >= call_times["search"]

    @pytest.mark.asyncio
    async def test_execute_parallel_with_callbacks(self):
        """测试带回调的并行执行"""
        tool_calls = [
            {"id": "1", "name": "test", "args": {}},
        ]

        started = []
        ended = []

        def on_start(name, args):
            started.append(name)

        def on_end(name, result):
            ended.append(name)

        async def mock_executor(name: str, args: dict) -> str:
            return "done"

        await self.scheduler.execute_parallel(
            tool_calls,
            mock_executor,
            on_tool_start=on_start,
            on_tool_end=on_end,
        )

        assert "test" in started
        assert "test" in ended

    @pytest.mark.asyncio
    async def test_execute_parallel_with_error(self):
        """测试执行错误处理"""
        tool_calls = [
            {"id": "1", "name": "failing_tool", "args": {}},
        ]

        errors = []

        def on_error(name, error):
            errors.append((name, error))

        async def mock_executor(name: str, args: dict) -> str:
            raise ValueError("Test error")

        # 设置重试次数为 0 以加快测试
        scheduler = ToolScheduler(retry_count=0)

        results = await scheduler.execute_parallel(
            tool_calls,
            mock_executor,
            on_tool_error=on_error,
        )

        assert len(errors) == 1
        assert "failing_tool" in errors[0][0]

    @pytest.mark.asyncio
    async def test_execute_tools_parallel_convenience(self):
        """测试便捷函数"""
        tool_calls = [
            {"id": "1", "name": "tool", "args": {"x": 1}},
        ]

        async def mock_executor(name: str, args: dict) -> int:
            return args["x"] * 2

        results = await execute_tools_parallel(tool_calls, mock_executor)

        assert results == [2]


# ============================================================
# ContextCompressor 测试
# ============================================================

class TestContextCompressor:
    """上下文压缩器测试类"""

    def setup_method(self):
        """每个测试方法前的设置"""
        self.compressor = ContextCompressor(llm=None, max_tokens=1000)

    def test_count_tokens_english(self):
        """测试英文 Token 计数"""
        text = "Hello world, this is a test."
        tokens = self.compressor._count_tokens(text)

        # 大约 28 个字符 / 4 = 7 tokens
        assert 5 <= tokens <= 10

    def test_count_tokens_chinese(self):
        """测试中文 Token 计数"""
        text = "你好世界，这是一个测试。"
        tokens = self.compressor._count_tokens(text)

        # 中文字符更多 token
        assert tokens > 5

    def test_count_tokens_mixed(self):
        """测试中英混合 Token 计数"""
        text = "Hello 你好 World 世界"
        tokens = self.compressor._count_tokens(text)

        assert tokens > 0

    def test_count_messages_tokens(self):
        """测试消息列表 Token 计数"""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]

        tokens = self.compressor._count_messages_tokens(messages)

        # 包含消息开销
        assert tokens > 0

    def test_calculate_importance_basic(self):
        """测试基本重要性计算"""
        message = {"role": "user", "content": "这是一个普通消息"}
        score = self.compressor._calculate_importance(message)

        assert 0 <= score <= 1

    def test_calculate_importance_high_keywords(self):
        """测试高重要性关键词"""
        message = {"role": "user", "content": "这是非常重要的信息，请记住"}
        score = self.compressor._calculate_importance(message)

        # 包含高重要性关键词，分数应该较高
        assert score > 0.6

    def test_calculate_importance_code(self):
        """测试代码内容的重要性"""
        message = {"role": "assistant", "content": "```python\ndef hello():\n    pass\n```"}
        score = self.compressor._calculate_importance(message)

        # 代码内容应该有较高重要性
        assert score > 0.5

    @pytest.mark.asyncio
    async def test_compress_empty(self):
        """测试空消息压缩"""
        result = await self.compressor.compress([])

        assert result.messages == []
        assert result.original_tokens == 0
        assert result.compression_ratio == 1.0

    @pytest.mark.asyncio
    async def test_compress_no_need(self):
        """测试不需要压缩的情况"""
        messages = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello!"},
        ]

        result = await self.compressor.compress(messages)

        # Token 数量未超过限制，不应压缩
        assert result.messages == messages
        assert result.compression_ratio == 1.0

    @pytest.mark.asyncio
    async def test_compress_truncate_strategy(self):
        """测试截断策略"""
        # 创建大量消息以触发压缩
        messages = [
            {"role": "user", "content": f"Message {i} " * 50}
            for i in range(20)
        ]

        compressor = ContextCompressor(llm=None, max_tokens=500)
        result = await compressor.compress(
            messages,
            strategy=CompressionStrategy.TRUNCATE,
        )

        assert len(result.messages) < len(messages)
        assert result.compression_ratio < 1.0

    @pytest.mark.asyncio
    async def test_compress_sliding_window_strategy(self):
        """测试滑动窗口策略"""
        messages = [
            {"role": "user", "content": f"Message {i} " * 50}
            for i in range(20)
        ]

        compressor = ContextCompressor(llm=None, max_tokens=500)
        result = await compressor.compress(
            messages,
            strategy=CompressionStrategy.SLIDING_WINDOW,
        )

        assert len(result.messages) < len(messages)
        # 滑动窗口应该保留最新的消息
        assert result.messages[-1]["content"] == messages[-1]["content"]

    @pytest.mark.asyncio
    async def test_compress_importance_based_strategy(self):
        """测试基于重要性的策略"""
        messages = [
            {"role": "user", "content": "普通消息 " * 50},
            {"role": "user", "content": "这是非常重要的信息 " * 50},
            {"role": "user", "content": "另一个普通消息 " * 50},
        ]

        compressor = ContextCompressor(llm=None, max_tokens=300, preserve_recent=1)
        result = await compressor.compress(
            messages,
            strategy=CompressionStrategy.IMPORTANCE_BASED,
        )

        assert len(result.messages) <= len(messages)

    @pytest.mark.asyncio
    async def test_compress_if_needed(self):
        """测试条件压缩"""
        messages = [
            {"role": "user", "content": "Short message"},
        ]

        result = await self.compressor.compress_if_needed(messages)

        # 不需要压缩，返回原始消息
        assert result == messages

    def test_estimate_remaining_capacity(self):
        """测试剩余容量估算"""
        messages = [
            {"role": "user", "content": "Test message"},
        ]

        capacity = self.compressor.estimate_remaining_capacity(messages)

        assert "current_tokens" in capacity
        assert "max_tokens" in capacity
        assert "remaining_tokens" in capacity
        assert "usage_ratio" in capacity
        assert "needs_compression" in capacity

    @pytest.mark.asyncio
    async def test_compress_context_convenience(self):
        """测试便捷函数"""
        messages = [
            {"role": "user", "content": "Hello"},
        ]

        result = await compress_context(messages, max_tokens=1000)

        assert result == messages


# ============================================================
# ToolCache 测试
# ============================================================

class TestToolCache:
    """工具缓存测试类"""

    def setup_method(self):
        """每个测试方法前的设置"""
        self.cache = ToolCache(default_ttl=60, max_size=100)
        clear_global_cache()

    def teardown_method(self):
        """每个测试方法后的清理"""
        self.cache.clear()

    def test_hash_args_consistency(self):
        """测试参数哈希一致性"""
        args1 = {"query": "test", "limit": 10}
        args2 = {"limit": 10, "query": "test"}  # 顺序不同

        hash1 = self.cache._hash_args("tool", args1)
        hash2 = self.cache._hash_args("tool", args2)

        # 相同参数应该产生相同哈希
        assert hash1 == hash2

    def test_hash_args_different(self):
        """测试不同参数产生不同哈希"""
        args1 = {"query": "test1"}
        args2 = {"query": "test2"}

        hash1 = self.cache._hash_args("tool", args1)
        hash2 = self.cache._hash_args("tool", args2)

        assert hash1 != hash2

    def test_set_and_get(self):
        """测试设置和获取缓存"""
        self.cache.set("search_engine", {"query": "AI"}, "result_data")

        result = self.cache.get("search_engine", {"query": "AI"})

        assert result == "result_data"

    def test_get_miss(self):
        """测试缓存未命中"""
        result = self.cache.get("nonexistent", {"arg": "value"})

        assert result is None

    def test_get_with_default(self):
        """测试带默认值的获取"""
        result = self.cache.get("nonexistent", {"arg": "value"}, default="default")

        assert result == "default"

    def test_ttl_expiration(self):
        """测试 TTL 过期"""
        cache = ToolCache(default_ttl=1)  # 1 秒过期
        cache.set("tool", {"arg": "value"}, "result")

        # 立即获取应该成功
        assert cache.get("tool", {"arg": "value"}) == "result"

        # 等待过期
        time.sleep(1.5)

        # 过期后应该返回 None
        assert cache.get("tool", {"arg": "value"}) is None

    def test_custom_ttl(self):
        """测试自定义 TTL"""
        self.cache.set("tool", {"arg": "value"}, "result", ttl=1)

        assert self.cache.get("tool", {"arg": "value"}) == "result"

        time.sleep(1.5)

        assert self.cache.get("tool", {"arg": "value"}) is None

    def test_delete(self):
        """测试删除缓存"""
        self.cache.set("tool", {"arg": "value"}, "result")

        assert self.cache.delete("tool", {"arg": "value"}) is True
        assert self.cache.get("tool", {"arg": "value"}) is None

    def test_delete_nonexistent(self):
        """测试删除不存在的缓存"""
        result = self.cache.delete("nonexistent", {"arg": "value"})

        assert result is False

    def test_clear(self):
        """测试清空缓存"""
        self.cache.set("tool1", {"arg": "1"}, "result1")
        self.cache.set("tool2", {"arg": "2"}, "result2")

        count = self.cache.clear()

        assert count == 2
        assert self.cache.get("tool1", {"arg": "1"}) is None
        assert self.cache.get("tool2", {"arg": "2"}) is None

    def test_clear_expired(self):
        """测试清理过期缓存"""
        cache = ToolCache(default_ttl=1)
        cache.set("tool1", {"arg": "1"}, "result1")
        cache.set("tool2", {"arg": "2"}, "result2", ttl=100)

        time.sleep(1.5)

        count = cache.clear_expired()

        assert count == 1
        assert cache.get("tool2", {"arg": "2"}) == "result2"

    def test_clear_by_tool(self):
        """测试按工具清除缓存"""
        self.cache.set("tool1", {"arg": "1"}, "result1")
        self.cache.set("tool1", {"arg": "2"}, "result2")
        self.cache.set("tool2", {"arg": "1"}, "result3")

        count = self.cache.clear_by_tool("tool1")

        assert count == 2
        assert self.cache.get("tool1", {"arg": "1"}) is None
        assert self.cache.get("tool2", {"arg": "1"}) == "result3"

    def test_exists(self):
        """测试缓存存在检查"""
        self.cache.set("tool", {"arg": "value"}, "result")

        assert self.cache.exists("tool", {"arg": "value"}) is True
        assert self.cache.exists("tool", {"arg": "other"}) is False

    def test_non_cacheable_tools(self):
        """测试不可缓存的工具"""
        # execute_python_code 不应该被缓存
        result = self.cache.set("execute_python_code", {"code": "print(1)"}, "output")

        assert result is False
        assert self.cache.get("execute_python_code", {"code": "print(1)"}) is None

    def test_lru_eviction(self):
        """测试 LRU 淘汰"""
        cache = ToolCache(default_ttl=60, max_size=3)

        cache.set("tool", {"id": "1"}, "result1")
        time.sleep(0.01)  # 确保时间戳不同
        cache.set("tool", {"id": "2"}, "result2")
        time.sleep(0.01)
        cache.set("tool", {"id": "3"}, "result3")

        # 访问第一个以更新其访问时间
        time.sleep(0.01)
        cache.get("tool", {"id": "1"})

        # 添加第四个，应该淘汰最少使用的(id=2，因为 id=1 刚被访问，id=3 是最新添加的)
        cache.set("tool", {"id": "4"}, "result4")

        # 第一个应该还在(最近访问过)
        assert cache.get("tool", {"id": "1"}) == "result1"
        # 第四个应该在
        assert cache.get("tool", {"id": "4"}) == "result4"
        # 验证缓存大小不超过限制
        info = cache.get_info()
        assert info["total_entries"] <= 3

    def test_get_stats(self):
        """测试获取统计信息"""
        self.cache.set("tool", {"arg": "1"}, "result")
        self.cache.get("tool", {"arg": "1"})  # hit
        self.cache.get("tool", {"arg": "2"})  # miss

        stats = self.cache.get_stats()

        assert stats is not None
        assert stats.total_hits >= 1
        assert stats.total_misses >= 1

    def test_get_info(self):
        """测试获取缓存信息"""
        self.cache.set("tool", {"arg": "value"}, "result")

        info = self.cache.get_info()

        assert "total_entries" in info
        assert "max_size" in info
        assert "hit_rate" in info

    def test_get_or_set(self):
        """测试 get_or_set"""
        call_count = 0

        def factory():
            nonlocal call_count
            call_count += 1
            return "generated_result"

        # 第一次调用应该执行工厂函数
        result1 = self.cache.get_or_set("tool", {"arg": "value"}, factory)
        assert result1 == "generated_result"
        assert call_count == 1

        # 第二次调用应该使用缓存
        result2 = self.cache.get_or_set("tool", {"arg": "value"}, factory)
        assert result2 == "generated_result"
        assert call_count == 1  # 工厂函数不应该再次调用

    @pytest.mark.asyncio
    async def test_get_or_set_async(self):
        """测试异步 get_or_set"""
        call_count = 0

        async def async_factory():
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.01)
            return "async_result"

        result1 = await self.cache.get_or_set_async("tool", {"arg": "value"}, async_factory)
        assert result1 == "async_result"
        assert call_count == 1

        result2 = await self.cache.get_or_set_async("tool", {"arg": "value"}, async_factory)
        assert result2 == "async_result"
        assert call_count == 1

    def test_cached_decorator_sync(self):
        """测试同步缓存装饰器"""
        call_count = 0

        @self.cache.cached(tool_name="decorated_tool")
        def my_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        result1 = my_function(5)
        assert result1 == 10
        assert call_count == 1

        result2 = my_function(5)
        assert result2 == 10
        assert call_count == 1  # 使用缓存

    @pytest.mark.asyncio
    async def test_cached_decorator_async(self):
        """测试异步缓存装饰器"""
        call_count = 0

        @self.cache.cached(tool_name="async_decorated_tool")
        async def my_async_function(x):
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.01)
            return x * 3

        result1 = await my_async_function(5)
        assert result1 == 15
        assert call_count == 1

        result2 = await my_async_function(5)
        assert result2 == 15
        assert call_count == 1

    def test_warmup(self):
        """测试缓存预热"""
        entries = [
            {"tool_name": "tool1", "args": {"a": 1}, "result": "r1"},
            {"tool_name": "tool2", "args": {"b": 2}, "result": "r2"},
        ]

        count = self.cache.warmup(entries)

        assert count == 2
        assert self.cache.get("tool1", {"a": 1}) == "r1"
        assert self.cache.get("tool2", {"b": 2}) == "r2"

    def test_export(self):
        """测试导出缓存"""
        self.cache.set("tool1", {"a": 1}, "result1")
        self.cache.set("tool2", {"b": 2}, "result2")

        exported = self.cache.export()

        assert len(exported) == 2
        assert all("tool_name" in e for e in exported)
        assert all("value" in e for e in exported)

    def test_global_cache(self):
        """测试全局缓存"""
        cache1 = get_tool_cache()
        cache2 = get_tool_cache()

        # 应该是同一个实例
        assert cache1 is cache2

        cache1.set("tool", {"arg": "value"}, "result")
        assert cache2.get("tool", {"arg": "value"}) == "result"

        clear_global_cache()


# ============================================================
# 集成测试
# ============================================================

class TestIntegration:
    """集成测试类"""

    @pytest.mark.asyncio
    async def test_scheduler_with_cache(self):
        """测试调度器与缓存的集成"""
        cache = ToolCache(default_ttl=60)
        scheduler = ToolScheduler(max_parallel=3)

        tool_calls = [
            {"id": "1", "name": "search_engine", "args": {"query": "test"}},
            {"id": "2", "name": "search_engine", "args": {"query": "test"}},  # 相同参数
        ]

        execution_count = 0

        async def cached_executor(name: str, args: dict) -> str:
            nonlocal execution_count

            # 检查缓存
            cached = cache.get(name, args)
            if cached is not None:
                return cached

            # 执行并缓存
            execution_count += 1
            result = f"result_for_{args.get('query')}"
            cache.set(name, args, result)
            return result

        results = await scheduler.execute_parallel(tool_calls, cached_executor)

        assert len(results) == 2
        # 由于并行执行，两个调用可能都执行了
        # 但后续相同调用应该使用缓存

        # 再次执行相同的调用
        results2 = await scheduler.execute_parallel(tool_calls, cached_executor)

        assert results2 == results

    @pytest.mark.asyncio
    async def test_compressor_with_scheduler(self):
        """测试压缩器与调度器的集成"""
        compressor = ContextCompressor(llm=None, max_tokens=500)

        # 模拟工具执行产生的消息
        messages = [
            {"role": "user", "content": "搜索 AI 相关信息"},
            {"role": "assistant", "content": "正在搜索..." + "x" * 200},
            {"role": "user", "content": "总结一下"},
            {"role": "assistant", "content": "总结如下..." + "y" * 200},
        ]

        # 压缩上下文
        result = await compressor.compress(messages)

        # 验证压缩结果
        assert result.compressed_tokens <= compressor.max_tokens
        assert len(result.messages) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
