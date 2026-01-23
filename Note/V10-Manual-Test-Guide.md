# V10 手动测试指南

> 本指南用于手动测试 V10 新增功能的完整流程

## 目录

1. [环境准备](#一环境准备)
2. [启动所有服务](#二启动所有服务)
3. [pptx-renderer-service 测试](#三pptx-renderer-service-测试)
4. [Agent 并行工具调用测试](#四agent-并行工具调用测试)
5. [RAG 查询改写测试](#五rag-查询改写测试)
6. [前端集成测试](#六前端集成测试)
7. [常见问题排查](#七常见问题排查)

---

## 一、环境准备

### 1.1 激活 Conda 环境

```bash
conda activate My-Chat-LangChain
```

### 1.2 配置环境变量

创建或编辑 `backend/.env` 文件：

```bash
# LLM API
GOOGLE_API_KEY=your-google-api-key

# 数据库 (本地测试用 SQLite)
DATABASE_URL=sqlite:///./test.db

# JWT
JWT_SECRET=your-secret-key-for-testing
JWT_ALGORITHM=HS256

# 可选: E2B 代码执行
E2B_API_KEY=your-e2b-api-key
```

### 1.3 安装依赖

```bash
# pptx-renderer-service 依赖
cd backend/pptx-renderer-service
pip install -r requirements.txt

# 安装 Playwright 浏览器 (首次运行)
playwright install chromium
```

---

## 二、启动所有服务

### 2.1 服务端口一览

| 服务 | 端口 | 说明 |
|------|------|------|
| frontend-next | 3000 | Next.js 前端 |
| auth-service | 8001 | 用户认证 |
| chat-service | 8002 | 聊天核心 (Agent) |
| whisper-service | 8003 | 语音识别 (可选) |
| rag-service | 8004 | RAG 检索 |
| presentation-service | 8005 | 演示文稿生成 |
| pptx-renderer | 8006 | PPTX 渲染 (V10 新增) |

### 2.2 启动后端服务

**方式一：分别启动（推荐调试时使用）**

打开多个终端窗口，分别执行：

```bash
# 终端 1: Auth 服务
cd backend/auth-service
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# 终端 2: Chat 服务
cd backend/chat-service
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

# 终端 3: RAG 服务
cd backend/rag-service
uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload

# 终端 4: Presentation 服务
cd backend/presentation-service
uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload

# 终端 5: PPTX Renderer 服务 (V10 新增)
cd backend/pptx-renderer-service
uvicorn app.main:app --host 0.0.0.0 --port 8006 --reload
```

**方式二：使用 Docker Compose**

```bash
docker-compose up -d
```

### 2.3 启动前端

```bash
cd frontend-next
npm install  # 首次运行
npm run dev
```

### 2.4 验证服务状态

```bash
# 检查各服务健康状态
curl http://127.0.0.1:8001/health  # auth-service
curl http://127.0.0.1:8002/health  # chat-service
curl http://127.0.0.1:8004/health  # rag-service
curl http://127.0.0.1:8005/health  # presentation-service
curl http://127.0.0.1:8006/health  # pptx-renderer (V10)
```

预期输出：`{"status":"healthy"}` 或类似响应

---

## 三、pptx-renderer-service 测试

### 3.1 健康检查

```bash
curl http://127.0.0.1:8006/health
```

预期输出：
```json
{"status": "healthy", "service": "pptx-renderer", "version": "1.0.0"}
```

### 3.2 渲染预览测试

**测试 1: 简单文本渲染**

```bash
curl -X POST http://127.0.0.1:8006/api/v1/render/preview/base64 \
  -H "Content-Type: application/json" \
  -d '{
    "html": "<div style=\"padding: 50px; font-size: 48px; color: #333; text-align: center;\"><h1 data-pptx-element=\"title\">测试标题</h1><p data-pptx-element=\"content\">这是内容文本</p></div>",
    "width": 1920,
    "height": 1080
  }'
```

预期输出：包含 base64 编码的 PNG 截图

**测试 2: 提取元素位置**

```bash
curl -X POST http://127.0.0.1:8006/api/v1/render/extract \
  -H "Content-Type: application/json" \
  -d '{
    "html": "<div data-pptx-element=\"title\" style=\"position:absolute;left:100px;top:50px;font-size:36px;\">标题</div><div data-pptx-element=\"content\" style=\"position:absolute;left:100px;top:150px;\">内容</div>"
  }'
```

预期输出：
```json
{
  "elements": [
    {"selector": "title", "x": 100, "y": 50, "width": ..., "height": ..., "text": "标题"},
    {"selector": "content", "x": 100, "y": 150, "width": ..., "height": ..., "text": "内容"}
  ]
}
```

### 3.3 生成 PPTX 测试

```bash
curl -X POST http://127.0.0.1:8006/api/v1/render \
  -H "Content-Type: application/json" \
  -d '{
    "html": "<div style=\"padding:50px;\"><h1 data-pptx-element=\"title\" style=\"font-size:48px;color:#2563eb;\">V10 测试演示</h1><p data-pptx-element=\"content\" style=\"font-size:24px;margin-top:30px;\">这是通过 pptx-renderer 生成的幻灯片</p></div>",
    "use_screenshot_background": true
  }' \
  --output test_v10.pptx
```

验证：用 PowerPoint 或 WPS 打开 `test_v10.pptx` 查看效果

### 3.4 多页幻灯片测试

```bash
curl -X POST http://127.0.0.1:8006/api/v1/render/multi \
  -H "Content-Type: application/json" \
  -d '{
    "slides": [
      {"html": "<h1 data-pptx-element=\"title\" style=\"font-size:48px;text-align:center;padding-top:200px;\">第一页：封面</h1>"},
      {"html": "<h2 data-pptx-element=\"title\" style=\"font-size:36px;\">第二页：内容</h2><ul data-pptx-element=\"content\"><li>要点 1</li><li>要点 2</li></ul>"},
      {"html": "<h2 data-pptx-element=\"title\" style=\"font-size:36px;text-align:center;padding-top:200px;\">第三页：谢谢</h2>"}
    ]
  }' \
  --output test_multi.pptx
```

---

## 四、Agent 并行工具调用测试

### 4.1 Python 交互式测试

```bash
cd backend/chat-service
python
```

```python
import asyncio
from app.services.tool_scheduler import ToolScheduler, ToolCall

# 创建调度器
scheduler = ToolScheduler()

# 定义工具调用
tool_calls = [
    ToolCall(id="1", name="search_web", args={"query": "Python 异步编程"}),
    ToolCall(id="2", name="search_arxiv", args={"query": "Large Language Model"}),
    ToolCall(id="3", name="summarize", args={"text": "$1.result", "depends_on": ["1"]})
]

# 分析依赖
deps = scheduler.analyze_dependencies(tool_calls)
print("依赖分析结果:")
print(f"  并行组: {deps['parallel_groups']}")
print(f"  依赖关系: {deps['dependencies']}")

# 预期输出:
# 依赖分析结果:
#   并行组: [['1', '2'], ['3']]
#   依赖关系: {'3': ['1']}
```

### 4.2 上下文压缩测试

```python
from app.services.context_compressor import ContextCompressor, CompressionStrategy

# 创建压缩器 (最大 500 tokens 用于测试)
compressor = ContextCompressor(max_tokens=500)

# 模拟长对话历史
messages = [
    {"role": "user", "content": "什么是机器学习？"},
    {"role": "assistant", "content": "机器学习是人工智能的一个分支，它使计算机能够从数据中学习并做出决策或预测，而无需明确编程。主要包括监督学习、无监督学习和强化学习三种类型。"},
    {"role": "user", "content": "监督学习有哪些常见算法？"},
    {"role": "assistant", "content": "监督学习的常见算法包括：线性回归、逻辑回归、决策树、随机森林、支持向量机(SVM)、K近邻(KNN)、朴素贝叶斯、神经网络等。"},
    {"role": "user", "content": "深度学习和机器学习有什么区别？"},
    {"role": "assistant", "content": "深度学习是机器学习的一个子集，主要区别在于：1) 深度学习使用多层神经网络；2) 深度学习能自动提取特征；3) 深度学习需要更多数据和计算资源。"},
    {"role": "user", "content": "能详细解释一下神经网络吗？"}
]

# 估算 token 数
token_count = compressor._count_tokens(messages)
print(f"原始消息 token 数: {token_count}")

# 压缩
result = asyncio.run(compressor.compress(messages, strategy=CompressionStrategy.TRUNCATE))
print(f"压缩后消息数: {len(result.messages)}")
print(f"压缩后 token 数: {result.compressed_tokens}")
print(f"压缩比: {result.compression_ratio:.2%}")
```

### 4.3 工具缓存测试

```python
from app.services.tool_cache import ToolCache
import time

# 创建缓存 (TTL 5秒用于测试)
cache = ToolCache(default_ttl=5)

# 设置缓存
cache.set("search_web", {"query": "Python"}, {"results": ["result1", "result2"]})
print("缓存已设置")

# 获取缓存
result = cache.get("search_web", {"query": "Python"})
print(f"获取缓存: {result}")

# 等待过期
print("等待 6 秒...")
time.sleep(6)

# 再次获取
result = cache.get("search_web", {"query": "Python"})
print(f"过期后获取: {result}")  # 应该是 None

# 查看统计
stats = cache.get_stats()
print(f"缓存统计: 命中={stats.hits}, 未命中={stats.misses}, 命中率={stats.hit_rate:.2%}")
```

---

## 五、RAG 查询改写测试

### 5.1 Python 交互式测试

```bash
cd backend/rag-service
python
```

```python
import asyncio
from app.services.query_rewriter import QueryRewriterService

# 创建服务
rewriter = QueryRewriterService()

# 测试 1: 检测是否需要改写
test_queries = [
    "它的实现原理是什么？",      # 需要改写 (包含"它")
    "这个方法怎么用？",          # 需要改写 (包含"这个")
    "RAG 是什么？",              # 不需要改写
    "刚才说的那个算法",          # 需要改写 (包含"刚才"、"那个")
]

for q in test_queries:
    needs = rewriter._needs_rewrite(q)
    print(f"'{q}' -> 需要改写: {needs}")
```

### 5.2 完整查询改写测试 (需要 API Key)

```python
import asyncio
import os

# 确保设置了 API Key
os.environ["GOOGLE_API_KEY"] = "your-api-key"

from app.services.query_rewriter import QueryRewriterService

rewriter = QueryRewriterService()

# 模拟对话历史
history = [
    {"role": "user", "content": "RAG 是什么？"},
    {"role": "assistant", "content": "RAG (Retrieval-Augmented Generation) 是检索增强生成技术，它结合了信息检索和文本生成，先从知识库中检索相关文档，再基于检索结果生成回答。"},
    {"role": "user", "content": "它有哪些应用场景？"},
    {"role": "assistant", "content": "RAG 的主要应用场景包括：问答系统、客服机器人、知识库查询、文档摘要等。"}
]

# 测试查询改写
async def test_rewrite():
    query = "它的实现原理是什么？"
    result = await rewriter.rewrite(query, history)

    print("=" * 50)
    print(f"原始查询: {query}")
    print(f"改写后: {result['main_query']}")
    print(f"变体: {result.get('variants', [])}")
    print(f"识别实体: {result.get('entities', [])}")
    print(f"改写理由: {result.get('reasoning', '')}")
    print("=" * 50)

asyncio.run(test_rewrite())
```

### 5.3 集成搜索测试

```python
# 测试带查询改写的搜索 (需要 RAG 服务完整配置)
from app.services.search_service import HybridSearchService

# 注意: 需要先配置向量数据库连接
# search_service = HybridSearchService(...)

# result = await search_service.search_with_rewrite(
#     query="它怎么实现的？",
#     conversation_history=history,
#     top_k=5
# )
# print(result)
```

---

## 六、前端集成测试

### 6.1 访问前端

打开浏览器访问: http://localhost:3000

### 6.2 用户认证测试

1. **注册新用户**
   - 点击"注册"
   - 填写用户名、邮箱、密码
   - 提交注册

2. **登录**
   - 使用注册的账号登录
   - 验证 JWT Token 是否正常工作

### 6.3 聊天功能测试

1. **基础对话**
   - 发送消息: "你好，介绍一下你自己"
   - 验证流式响应是否正常

2. **多轮对话 (测试查询改写)**
   - 第一轮: "RAG 是什么技术？"
   - 第二轮: "它有什么优点？" (测试指代消解)
   - 第三轮: "具体怎么实现？"

3. **工具调用测试**
   - 发送: "搜索一下最新的 AI 新闻"
   - 验证工具调用是否正常

### 6.4 演示文稿功能测试

1. **创建演示文稿**
   - 进入演示文稿页面
   - 发送: "帮我创建一个关于人工智能的 5 页 PPT"

2. **预览和编辑**
   - 查看生成的幻灯片预览
   - 测试主题切换
   - 测试布局调整

3. **导出测试**
   - 点击"导出 HTML"
   - 点击"导出 PPTX" (如果 pptx-renderer 服务已启动)

### 6.5 RAG 文档功能测试

1. **上传文档**
   - 上传一个 PDF 或 TXT 文件
   - 等待解析完成

2. **基于文档问答**
   - 发送与文档相关的问题
   - 验证是否返回引用来源

---

## 七、常见问题排查

### 7.1 服务无法启动

**问题**: `Address already in use`

```bash
# 查找占用端口的进程
netstat -ano | findstr ":8006"

# 杀掉进程
taskkill /PID <进程ID> /F
```

### 7.2 Playwright 浏览器未安装

**问题**: `Browser not found`

```bash
# 安装 Chromium
playwright install chromium
```

### 7.3 API Key 未配置

**问题**: `GOOGLE_API_KEY not set`

```bash
# Windows
set GOOGLE_API_KEY=your-api-key

# Linux/Mac
export GOOGLE_API_KEY=your-api-key
```

### 7.4 前端无法连接后端

**问题**: 502 Bad Gateway 或连接超时

1. 检查后端服务是否启动
2. 检查是否有代理软件拦截 (如 Clash)
3. 在 Clash 中添加规则: `DOMAIN-SUFFIX,127.0.0.1,DIRECT`

### 7.5 PPTX 生成失败

**问题**: 生成的 PPTX 为空或损坏

1. 检查 pptx-renderer 服务日志
2. 确认 Playwright 浏览器已安装
3. 检查 HTML 中是否包含 `data-pptx-element` 属性

---

## 测试检查清单

| 功能 | 测试项 | 状态 |
|------|--------|------|
| **pptx-renderer** | 健康检查 | ☐ |
| | 预览截图 | ☐ |
| | 元素位置提取 | ☐ |
| | 单页 PPTX 生成 | ☐ |
| | 多页 PPTX 生成 | ☐ |
| **Agent 并行** | 依赖分析 | ☐ |
| | 并行执行 | ☐ |
| | 上下文压缩 | ☐ |
| | 工具缓存 | ☐ |
| **RAG 查询改写** | 指代词检测 | ☐ |
| | 查询改写 | ☐ |
| | 集成搜索 | ☐ |
| **前端** | 用户认证 | ☐ |
| | 聊天对话 | ☐ |
| | 演示文稿 | ☐ |
| | 文档上传 | ☐ |

---

> **文档版本**: 1.0
> **最后更新**: 2026-01-24
> **适用版本**: V10.0
