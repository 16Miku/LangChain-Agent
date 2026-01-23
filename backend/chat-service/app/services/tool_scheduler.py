# ============================================================
# Chat Service - Tool Scheduler
# 工具调用调度器 - 分析依赖并并行执行
# ============================================================

import asyncio
import hashlib
import json
import re
from typing import List, Dict, Any, Optional, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ToolStatus(Enum):
    """工具执行状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ToolCall:
    """工具调用数据结构"""
    id: str
    name: str
    args: Dict[str, Any]
    status: ToolStatus = ToolStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    dependencies: Set[str] = field(default_factory=set)

    def __hash__(self):
        return hash(self.id)


@dataclass
class ExecutionPlan:
    """执行计划数据结构"""
    parallel_groups: List[List[str]]  # 可并行执行的工具组
    dependencies: Dict[str, List[str]]  # 工具依赖关系
    execution_order: List[str]  # 执行顺序
    total_tools: int


class ToolScheduler:
    """
    工具调用调度器 - 分析依赖并并行执行

    功能:
    1. 分析工具调用之间的依赖关系
    2. 生成最优执行计划
    3. 并行执行无依赖的工具调用
    4. 处理执行失败和重试

    使用示例:
    ```python
    scheduler = ToolScheduler(max_parallel=5)

    tool_calls = [
        {"id": "1", "name": "search", "args": {"query": "AI"}},
        {"id": "2", "name": "search", "args": {"query": "ML"}},
        {"id": "3", "name": "summarize", "args": {"text": "$1.result"}},
    ]

    results = await scheduler.execute_parallel(tool_calls, tool_executor)
    ```
    """

    # 工具依赖规则: 某些工具的输出可能被其他工具使用
    DEPENDENCY_PATTERNS = {
        # 搜索结果可能被摘要工具使用
        "summarize": ["search", "scrape", "rag_search"],
        # 分析工具可能依赖数据获取工具
        "analyze": ["search", "scrape", "fetch", "rag_search"],
        # 代码执行可能依赖数据上传
        "execute_python_code": ["upload_data_to_sandbox"],
        # CSV 分析依赖数据上传
        "analyze_csv_data": ["upload_data_to_sandbox"],
    }

    # 可以安全并行执行的工具类型
    PARALLELIZABLE_TOOLS = {
        "search_engine",
        "scrape_as_markdown",
        "scrape_as_html",
        "rag_search",
        "web_data_linkedin_person_profile",
        "web_data_linkedin_company_profile",
        "web_data_instagram_profiles",
        "web_data_facebook_posts",
        "web_data_x_posts",
        "web_data_youtube_videos",
        "arxiv_search",
        "pubmed_search",
    }

    def __init__(
        self,
        max_parallel: int = 5,
        timeout: float = 60.0,
        retry_count: int = 2,
        retry_delay: float = 1.0,
    ):
        """
        初始化工具调度器

        Args:
            max_parallel: 最大并行执行数量
            timeout: 单个工具执行超时时间(秒)
            retry_count: 失败重试次数
            retry_delay: 重试延迟时间(秒)
        """
        self.max_parallel = max_parallel
        self.timeout = timeout
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self._semaphore: Optional[asyncio.Semaphore] = None

    def _parse_tool_calls(self, tool_calls: List[Dict]) -> List[ToolCall]:
        """
        解析工具调用列表

        Args:
            tool_calls: 原始工具调用列表

        Returns:
            解析后的 ToolCall 对象列表
        """
        parsed = []
        for i, call in enumerate(tool_calls):
            tool_id = call.get("id", f"tool_{i}")
            parsed.append(ToolCall(
                id=tool_id,
                name=call.get("name", ""),
                args=call.get("args", {}),
            ))
        return parsed

    def _detect_arg_dependencies(self, args: Dict[str, Any]) -> Set[str]:
        """
        检测参数中的依赖引用

        支持的引用格式:
        - $tool_id.result: 引用某个工具的结果
        - ${tool_id}.field: 引用某个工具结果的特定字段

        Args:
            args: 工具参数

        Returns:
            依赖的工具 ID 集合
        """
        dependencies = set()

        # 递归检查所有参数值
        def check_value(value):
            if isinstance(value, str):
                # 匹配 $tool_id.result 或 ${tool_id}.field 格式
                patterns = [
                    r'\$(\w+)\.result',
                    r'\$\{(\w+)\}',
                    r'\$(\w+)',
                ]
                for pattern in patterns:
                    matches = re.findall(pattern, value)
                    dependencies.update(matches)
            elif isinstance(value, dict):
                for v in value.values():
                    check_value(v)
            elif isinstance(value, list):
                for item in value:
                    check_value(item)

        for arg_value in args.values():
            check_value(arg_value)

        return dependencies

    def _detect_implicit_dependencies(
        self,
        tool: ToolCall,
        all_tools: List[ToolCall],
    ) -> Set[str]:
        """
        检测隐式依赖关系

        基于工具类型和执行顺序推断依赖

        Args:
            tool: 当前工具
            all_tools: 所有工具列表

        Returns:
            隐式依赖的工具 ID 集合
        """
        dependencies = set()

        # 检查是否有预定义的依赖规则
        for dependent_tool, source_tools in self.DEPENDENCY_PATTERNS.items():
            if dependent_tool in tool.name.lower():
                # 查找之前的源工具
                for other_tool in all_tools:
                    if other_tool.id == tool.id:
                        continue
                    for source in source_tools:
                        if source in other_tool.name.lower():
                            dependencies.add(other_tool.id)

        return dependencies

    def analyze_dependencies(self, tool_calls: List[Dict]) -> Dict[str, Any]:
        """
        分析工具调用之间的依赖关系

        Args:
            tool_calls: 工具调用列表，每个元素包含:
                - id: 工具调用 ID
                - name: 工具名称
                - args: 工具参数

        Returns:
            依赖分析结果:
            {
                "parallel_groups": [["tool1", "tool2"], ["tool3"]],
                "dependencies": {"tool3": ["tool1", "tool2"]},
                "execution_order": ["tool1", "tool2", "tool3"],
                "total_tools": 3
            }
        """
        if not tool_calls:
            return {
                "parallel_groups": [],
                "dependencies": {},
                "execution_order": [],
                "total_tools": 0,
            }

        # 解析工具调用
        tools = self._parse_tool_calls(tool_calls)
        tool_map = {t.id: t for t in tools}

        # 分析每个工具的依赖
        for tool in tools:
            # 显式依赖(参数引用)
            explicit_deps = self._detect_arg_dependencies(tool.args)
            # 隐式依赖(工具类型推断)
            implicit_deps = self._detect_implicit_dependencies(tool, tools)
            # 合并依赖
            tool.dependencies = explicit_deps | implicit_deps
            # 过滤无效依赖
            tool.dependencies = {d for d in tool.dependencies if d in tool_map}

        # 拓扑排序生成执行顺序
        execution_order = self._topological_sort(tools)

        # 生成并行执行组
        parallel_groups = self._generate_parallel_groups(tools, execution_order)

        # 构建依赖字典
        dependencies = {
            t.id: list(t.dependencies)
            for t in tools
            if t.dependencies
        }

        return {
            "parallel_groups": parallel_groups,
            "dependencies": dependencies,
            "execution_order": execution_order,
            "total_tools": len(tools),
        }

    def _topological_sort(self, tools: List[ToolCall]) -> List[str]:
        """
        拓扑排序生成执行顺序

        Args:
            tools: 工具列表

        Returns:
            排序后的工具 ID 列表
        """
        # 计算入度
        in_degree = {t.id: len(t.dependencies) for t in tools}
        tool_map = {t.id: t for t in tools}

        # 找出所有入度为 0 的节点
        queue = [t.id for t in tools if in_degree[t.id] == 0]
        result = []

        while queue:
            # 按工具名称排序以保证稳定性
            queue.sort()
            current = queue.pop(0)
            result.append(current)

            # 更新依赖当前节点的工具的入度
            for tool in tools:
                if current in tool.dependencies:
                    in_degree[tool.id] -= 1
                    if in_degree[tool.id] == 0:
                        queue.append(tool.id)

        # 检查是否有循环依赖
        if len(result) != len(tools):
            logger.warning("检测到循环依赖，部分工具可能无法执行")
            # 添加未处理的工具
            remaining = [t.id for t in tools if t.id not in result]
            result.extend(remaining)

        return result

    def _generate_parallel_groups(
        self,
        tools: List[ToolCall],
        execution_order: List[str],
    ) -> List[List[str]]:
        """
        生成并行执行组

        将可以同时执行的工具分组

        Args:
            tools: 工具列表
            execution_order: 执行顺序

        Returns:
            并行执行组列表
        """
        tool_map = {t.id: t for t in tools}
        completed = set()
        groups = []

        remaining = set(execution_order)

        while remaining:
            # 找出当前可以执行的工具(依赖已完成)
            current_group = []
            for tool_id in execution_order:
                if tool_id not in remaining:
                    continue
                tool = tool_map[tool_id]
                # 检查所有依赖是否已完成
                if tool.dependencies.issubset(completed):
                    current_group.append(tool_id)

            if not current_group:
                # 无法继续，可能有循环依赖
                current_group = list(remaining)[:1]

            groups.append(current_group)
            completed.update(current_group)
            remaining -= set(current_group)

        return groups

    def _resolve_arg_references(
        self,
        args: Dict[str, Any],
        results: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        解析参数中的引用，替换为实际结果

        Args:
            args: 原始参数
            results: 已完成工具的结果

        Returns:
            解析后的参数
        """
        def resolve_value(value):
            if isinstance(value, str):
                # 替换 $tool_id.result 引用
                for tool_id, result in results.items():
                    value = value.replace(f"${tool_id}.result", str(result))
                    value = value.replace(f"${{{tool_id}}}", str(result))
                    value = value.replace(f"${tool_id}", str(result))
                return value
            elif isinstance(value, dict):
                return {k: resolve_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [resolve_value(item) for item in value]
            return value

        return {k: resolve_value(v) for k, v in args.items()}

    async def _execute_single_tool(
        self,
        tool: ToolCall,
        tool_executor: Callable,
        results: Dict[str, Any],
    ) -> Any:
        """
        执行单个工具调用

        Args:
            tool: 工具调用
            tool_executor: 工具执行器函数
            results: 已完成工具的结果

        Returns:
            工具执行结果
        """
        # 解析参数引用
        resolved_args = self._resolve_arg_references(tool.args, results)

        # 使用信号量限制并发
        async with self._semaphore:
            tool.status = ToolStatus.RUNNING

            for attempt in range(self.retry_count + 1):
                try:
                    # 执行工具
                    result = await asyncio.wait_for(
                        tool_executor(tool.name, resolved_args),
                        timeout=self.timeout,
                    )
                    tool.status = ToolStatus.COMPLETED
                    tool.result = result
                    return result

                except asyncio.TimeoutError:
                    tool.error = f"工具执行超时 ({self.timeout}秒)"
                    logger.warning(f"工具 {tool.name} 执行超时，尝试 {attempt + 1}/{self.retry_count + 1}")

                except Exception as e:
                    tool.error = str(e)
                    logger.warning(f"工具 {tool.name} 执行失败: {e}，尝试 {attempt + 1}/{self.retry_count + 1}")

                # 重试延迟
                if attempt < self.retry_count:
                    await asyncio.sleep(self.retry_delay)

            # 所有重试都失败
            tool.status = ToolStatus.FAILED
            raise RuntimeError(f"工具 {tool.name} 执行失败: {tool.error}")

    async def execute_parallel(
        self,
        tool_calls: List[Dict],
        tool_executor: Callable,
        on_tool_start: Optional[Callable[[str, Dict], None]] = None,
        on_tool_end: Optional[Callable[[str, Any], None]] = None,
        on_tool_error: Optional[Callable[[str, str], None]] = None,
    ) -> List[Any]:
        """
        并行执行工具调用

        Args:
            tool_calls: 工具调用列表
            tool_executor: 工具执行器函数，签名: async (name, args) -> result
            on_tool_start: 工具开始执行回调
            on_tool_end: 工具执行完成回调
            on_tool_error: 工具执行错误回调

        Returns:
            按原始顺序排列的执行结果列表
        """
        if not tool_calls:
            return []

        # 初始化信号量
        self._semaphore = asyncio.Semaphore(self.max_parallel)

        # 分析依赖
        plan = self.analyze_dependencies(tool_calls)

        # 解析工具调用
        tools = self._parse_tool_calls(tool_calls)
        tool_map = {t.id: t for t in tools}

        # 存储结果
        results: Dict[str, Any] = {}

        # 按组执行
        for group in plan["parallel_groups"]:
            # 创建当前组的任务
            tasks = []
            for tool_id in group:
                tool = tool_map[tool_id]

                # 回调: 工具开始
                if on_tool_start:
                    on_tool_start(tool.name, tool.args)

                # 创建执行任务
                task = asyncio.create_task(
                    self._execute_single_tool(tool, tool_executor, results)
                )
                tasks.append((tool_id, tool, task))

            # 等待当前组完成
            for tool_id, tool, task in tasks:
                try:
                    result = await task
                    results[tool_id] = result

                    # 回调: 工具完成
                    if on_tool_end:
                        on_tool_end(tool.name, result)

                except Exception as e:
                    results[tool_id] = None

                    # 回调: 工具错误
                    if on_tool_error:
                        on_tool_error(tool.name, str(e))

        # 按原始顺序返回结果
        return [results.get(t.id) for t in tools]

    def create_execution_plan(self, tool_calls: List[Dict]) -> ExecutionPlan:
        """
        创建执行计划对象

        Args:
            tool_calls: 工具调用列表

        Returns:
            ExecutionPlan 对象
        """
        analysis = self.analyze_dependencies(tool_calls)
        return ExecutionPlan(
            parallel_groups=analysis["parallel_groups"],
            dependencies=analysis["dependencies"],
            execution_order=analysis["execution_order"],
            total_tools=analysis["total_tools"],
        )


# 便捷函数
async def execute_tools_parallel(
    tool_calls: List[Dict],
    tool_executor: Callable,
    max_parallel: int = 5,
) -> List[Any]:
    """
    便捷函数: 并行执行工具调用

    Args:
        tool_calls: 工具调用列表
        tool_executor: 工具执行器
        max_parallel: 最大并行数

    Returns:
        执行结果列表
    """
    scheduler = ToolScheduler(max_parallel=max_parallel)
    return await scheduler.execute_parallel(tool_calls, tool_executor)
