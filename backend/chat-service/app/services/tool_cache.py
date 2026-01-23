# ============================================================
# Chat Service - Tool Cache
# 工具调用缓存 - 缓存工具执行结果以提高性能
# ============================================================

import asyncio
import hashlib
import json
import time
from typing import Optional, Any, Dict, List, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
import threading

logger = logging.getLogger(__name__)


class CacheStatus(Enum):
    """缓存状态枚举"""
    HIT = "hit"  # 缓存命中
    MISS = "miss"  # 缓存未命中
    EXPIRED = "expired"  # 缓存已过期
    INVALIDATED = "invalidated"  # 缓存已失效


@dataclass
class CacheEntry:
    """缓存条目数据结构"""
    key: str
    value: Any
    created_at: float
    expires_at: float
    hit_count: int = 0
    last_accessed: float = field(default_factory=time.time)
    tool_name: str = ""
    args_hash: str = ""

    @property
    def is_expired(self) -> bool:
        """检查是否已过期"""
        return time.time() > self.expires_at

    @property
    def ttl_remaining(self) -> float:
        """剩余生存时间(秒)"""
        return max(0, self.expires_at - time.time())


@dataclass
class CacheStats:
    """缓存统计数据"""
    total_hits: int = 0
    total_misses: int = 0
    total_entries: int = 0
    total_expired: int = 0
    total_invalidated: int = 0
    memory_usage_bytes: int = 0

    @property
    def hit_rate(self) -> float:
        """缓存命中率"""
        total = self.total_hits + self.total_misses
        return self.total_hits / total if total > 0 else 0.0


class ToolCache:
    """
    工具调用缓存

    功能:
    1. 缓存工具执行结果
    2. 支持 TTL 过期机制
    3. 支持 LRU 淘汰策略
    4. 线程安全
    5. 支持缓存预热和批量操作

    使用示例:
    ```python
    cache = ToolCache(default_ttl=300, max_size=1000)

    # 设置缓存
    cache.set("search_engine", {"query": "AI"}, result)

    # 获取缓存
    cached = cache.get("search_engine", {"query": "AI"})

    # 使用装饰器
    @cache.cached(ttl=600)
    async def search(query: str):
        return await do_search(query)
    ```
    """

    # 不应该缓存的工具(结果时效性强)
    NON_CACHEABLE_TOOLS = {
        "execute_python_code",  # 代码执行结果可能不同
        "execute_shell_command",  # Shell 命令结果可能不同
        "upload_data_to_sandbox",  # 上传操作
        "download_file_from_sandbox",  # 下载操作
    }

    # 工具特定的 TTL 配置(秒)
    TOOL_TTL_CONFIG = {
        # 搜索结果缓存较短时间
        "search_engine": 300,  # 5 分钟
        "scrape_as_markdown": 600,  # 10 分钟
        "scrape_as_html": 600,  # 10 分钟

        # 社交媒体数据缓存中等时间
        "web_data_linkedin_person_profile": 3600,  # 1 小时
        "web_data_linkedin_company_profile": 3600,  # 1 小时
        "web_data_instagram_profiles": 1800,  # 30 分钟
        "web_data_x_posts": 300,  # 5 分钟

        # RAG 搜索结果缓存较长时间(文档不常变)
        "rag_search": 1800,  # 30 分钟
        "list_knowledge_documents": 3600,  # 1 小时

        # 学术搜索缓存较长时间
        "arxiv_search": 3600,  # 1 小时
        "pubmed_search": 3600,  # 1 小时
    }

    def __init__(
        self,
        default_ttl: int = 300,
        max_size: int = 1000,
        cleanup_interval: int = 60,
        enable_stats: bool = True,
    ):
        """
        初始化工具缓存

        Args:
            default_ttl: 默认缓存生存时间(秒)
            max_size: 最大缓存条目数
            cleanup_interval: 清理间隔(秒)
            enable_stats: 是否启用统计
        """
        self.default_ttl = default_ttl
        self.max_size = max_size
        self.cleanup_interval = cleanup_interval
        self.enable_stats = enable_stats

        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        self._stats = CacheStats() if enable_stats else None

        # 启动后台清理任务
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False

    def _hash_args(self, tool_name: str, args: dict) -> str:
        """
        生成参数哈希

        Args:
            tool_name: 工具名称
            args: 工具参数

        Returns:
            哈希字符串
        """
        # 规范化参数(排序键，处理特殊类型)
        normalized = self._normalize_args(args)

        # 生成哈希
        content = f"{tool_name}:{json.dumps(normalized, sort_keys=True, ensure_ascii=False)}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _normalize_args(self, args: Any) -> Any:
        """
        规范化参数以确保一致的哈希

        Args:
            args: 原始参数

        Returns:
            规范化后的参数
        """
        if isinstance(args, dict):
            return {k: self._normalize_args(v) for k, v in sorted(args.items())}
        elif isinstance(args, list):
            return [self._normalize_args(item) for item in args]
        elif isinstance(args, (set, frozenset)):
            return sorted(self._normalize_args(item) for item in args)
        elif isinstance(args, (int, float, str, bool, type(None))):
            return args
        else:
            return str(args)

    def _generate_key(self, tool_name: str, args: dict) -> str:
        """
        生成缓存键

        Args:
            tool_name: 工具名称
            args: 工具参数

        Returns:
            缓存键
        """
        args_hash = self._hash_args(tool_name, args)
        return f"{tool_name}:{args_hash}"

    def _get_ttl(self, tool_name: str, custom_ttl: Optional[int] = None) -> int:
        """
        获取工具的 TTL

        Args:
            tool_name: 工具名称
            custom_ttl: 自定义 TTL

        Returns:
            TTL 秒数
        """
        if custom_ttl is not None:
            return custom_ttl
        return self.TOOL_TTL_CONFIG.get(tool_name, self.default_ttl)

    def _is_cacheable(self, tool_name: str) -> bool:
        """
        检查工具是否可缓存

        Args:
            tool_name: 工具名称

        Returns:
            是否可缓存
        """
        return tool_name not in self.NON_CACHEABLE_TOOLS

    def _evict_lru(self) -> None:
        """
        LRU 淘汰策略

        移除最近最少使用的条目
        """
        if len(self._cache) <= self.max_size:
            return

        # 按最后访问时间排序
        sorted_entries = sorted(
            self._cache.items(),
            key=lambda x: x[1].last_accessed,
        )

        # 移除最旧的条目
        entries_to_remove = len(self._cache) - self.max_size
        for key, _ in sorted_entries[:entries_to_remove]:
            del self._cache[key]
            if self._stats:
                self._stats.total_invalidated += 1

    def get(
        self,
        tool_name: str,
        args: dict,
        default: Any = None,
    ) -> Optional[Any]:
        """
        获取缓存结果

        Args:
            tool_name: 工具名称
            args: 工具参数
            default: 默认值

        Returns:
            缓存的结果或默认值
        """
        if not self._is_cacheable(tool_name):
            if self._stats:
                self._stats.total_misses += 1
            return default

        key = self._generate_key(tool_name, args)

        with self._lock:
            entry = self._cache.get(key)

            if entry is None:
                if self._stats:
                    self._stats.total_misses += 1
                return default

            if entry.is_expired:
                del self._cache[key]
                if self._stats:
                    self._stats.total_expired += 1
                    self._stats.total_misses += 1
                return default

            # 更新访问信息
            entry.hit_count += 1
            entry.last_accessed = time.time()

            if self._stats:
                self._stats.total_hits += 1

            return entry.value

    def set(
        self,
        tool_name: str,
        args: dict,
        result: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """
        设置缓存

        Args:
            tool_name: 工具名称
            args: 工具参数
            result: 执行结果
            ttl: 自定义 TTL(秒)

        Returns:
            是否成功设置
        """
        if not self._is_cacheable(tool_name):
            return False

        key = self._generate_key(tool_name, args)
        actual_ttl = self._get_ttl(tool_name, ttl)
        now = time.time()

        entry = CacheEntry(
            key=key,
            value=result,
            created_at=now,
            expires_at=now + actual_ttl,
            tool_name=tool_name,
            args_hash=self._hash_args(tool_name, args),
        )

        with self._lock:
            self._cache[key] = entry
            self._evict_lru()

            if self._stats:
                self._stats.total_entries = len(self._cache)

        return True

    def delete(self, tool_name: str, args: dict) -> bool:
        """
        删除缓存条目

        Args:
            tool_name: 工具名称
            args: 工具参数

        Returns:
            是否成功删除
        """
        key = self._generate_key(tool_name, args)

        with self._lock:
            if key in self._cache:
                del self._cache[key]
                if self._stats:
                    self._stats.total_invalidated += 1
                    self._stats.total_entries = len(self._cache)
                return True
        return False

    def clear(self) -> int:
        """
        清空所有缓存

        Returns:
            清除的条目数
        """
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            if self._stats:
                self._stats.total_entries = 0
            return count

    def clear_expired(self) -> int:
        """
        清理过期缓存

        Returns:
            清除的条目数
        """
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired
            ]

            for key in expired_keys:
                del self._cache[key]

            if self._stats:
                self._stats.total_expired += len(expired_keys)
                self._stats.total_entries = len(self._cache)

            return len(expired_keys)

    def clear_by_tool(self, tool_name: str) -> int:
        """
        清除特定工具的所有缓存

        Args:
            tool_name: 工具名称

        Returns:
            清除的条目数
        """
        with self._lock:
            keys_to_remove = [
                key for key, entry in self._cache.items()
                if entry.tool_name == tool_name
            ]

            for key in keys_to_remove:
                del self._cache[key]

            if self._stats:
                self._stats.total_invalidated += len(keys_to_remove)
                self._stats.total_entries = len(self._cache)

            return len(keys_to_remove)

    def get_stats(self) -> Optional[CacheStats]:
        """
        获取缓存统计

        Returns:
            CacheStats 对象或 None
        """
        if not self._stats:
            return None

        with self._lock:
            self._stats.total_entries = len(self._cache)
            # 估算内存使用
            self._stats.memory_usage_bytes = sum(
                len(str(entry.value).encode()) for entry in self._cache.values()
            )
        return self._stats

    def get_info(self) -> Dict[str, Any]:
        """
        获取缓存信息

        Returns:
            缓存信息字典
        """
        with self._lock:
            stats = self.get_stats()
            return {
                "total_entries": len(self._cache),
                "max_size": self.max_size,
                "default_ttl": self.default_ttl,
                "hit_rate": stats.hit_rate if stats else 0,
                "total_hits": stats.total_hits if stats else 0,
                "total_misses": stats.total_misses if stats else 0,
                "memory_usage_bytes": stats.memory_usage_bytes if stats else 0,
            }

    def exists(self, tool_name: str, args: dict) -> bool:
        """
        检查缓存是否存在且有效

        Args:
            tool_name: 工具名称
            args: 工具参数

        Returns:
            是否存在有效缓存
        """
        key = self._generate_key(tool_name, args)

        with self._lock:
            entry = self._cache.get(key)
            return entry is not None and not entry.is_expired

    def get_or_set(
        self,
        tool_name: str,
        args: dict,
        factory: Callable[[], Any],
        ttl: Optional[int] = None,
    ) -> Any:
        """
        获取缓存，如果不存在则设置

        Args:
            tool_name: 工具名称
            args: 工具参数
            factory: 生成值的工厂函数
            ttl: 自定义 TTL

        Returns:
            缓存值或新生成的值
        """
        cached = self.get(tool_name, args)
        if cached is not None:
            return cached

        result = factory()
        self.set(tool_name, args, result, ttl)
        return result

    async def get_or_set_async(
        self,
        tool_name: str,
        args: dict,
        factory: Callable[[], Any],
        ttl: Optional[int] = None,
    ) -> Any:
        """
        异步版本的 get_or_set

        Args:
            tool_name: 工具名称
            args: 工具参数
            factory: 异步工厂函数
            ttl: 自定义 TTL

        Returns:
            缓存值或新生成的值
        """
        cached = self.get(tool_name, args)
        if cached is not None:
            return cached

        result = await factory()
        self.set(tool_name, args, result, ttl)
        return result

    def cached(
        self,
        tool_name: Optional[str] = None,
        ttl: Optional[int] = None,
    ) -> Callable:
        """
        缓存装饰器

        Args:
            tool_name: 工具名称(默认使用函数名)
            ttl: 自定义 TTL

        Returns:
            装饰器函数
        """
        def decorator(func: Callable) -> Callable:
            actual_tool_name = tool_name or func.__name__

            async def async_wrapper(*args, **kwargs):
                cache_args = {"args": args, "kwargs": kwargs}
                cached = self.get(actual_tool_name, cache_args)
                if cached is not None:
                    return cached

                result = await func(*args, **kwargs)
                self.set(actual_tool_name, cache_args, result, ttl)
                return result

            def sync_wrapper(*args, **kwargs):
                cache_args = {"args": args, "kwargs": kwargs}
                cached = self.get(actual_tool_name, cache_args)
                if cached is not None:
                    return cached

                result = func(*args, **kwargs)
                self.set(actual_tool_name, cache_args, result, ttl)
                return result

            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            return sync_wrapper

        return decorator

    async def start_cleanup_task(self) -> None:
        """启动后台清理任务"""
        if self._running:
            return

        self._running = True

        async def cleanup_loop():
            while self._running:
                await asyncio.sleep(self.cleanup_interval)
                self.clear_expired()

        self._cleanup_task = asyncio.create_task(cleanup_loop())

    async def stop_cleanup_task(self) -> None:
        """停止后台清理任务"""
        self._running = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None

    def warmup(self, entries: List[Dict[str, Any]]) -> int:
        """
        缓存预热

        Args:
            entries: 预热条目列表，每个条目包含:
                - tool_name: 工具名称
                - args: 工具参数
                - result: 结果
                - ttl: 可选 TTL

        Returns:
            成功预热的条目数
        """
        count = 0
        for entry in entries:
            success = self.set(
                entry["tool_name"],
                entry["args"],
                entry["result"],
                entry.get("ttl"),
            )
            if success:
                count += 1
        return count

    def export(self) -> List[Dict[str, Any]]:
        """
        导出缓存数据

        Returns:
            缓存条目列表
        """
        with self._lock:
            return [
                {
                    "tool_name": entry.tool_name,
                    "args_hash": entry.args_hash,
                    "value": entry.value,
                    "created_at": entry.created_at,
                    "expires_at": entry.expires_at,
                    "hit_count": entry.hit_count,
                }
                for entry in self._cache.values()
                if not entry.is_expired
            ]


# 全局缓存实例
_global_cache: Optional[ToolCache] = None


def get_tool_cache(
    default_ttl: int = 300,
    max_size: int = 1000,
) -> ToolCache:
    """
    获取全局工具缓存实例

    Args:
        default_ttl: 默认 TTL
        max_size: 最大大小

    Returns:
        ToolCache 实例
    """
    global _global_cache
    if _global_cache is None:
        _global_cache = ToolCache(default_ttl=default_ttl, max_size=max_size)
    return _global_cache


def clear_global_cache() -> None:
    """清空全局缓存"""
    global _global_cache
    if _global_cache:
        _global_cache.clear()
        _global_cache = None
