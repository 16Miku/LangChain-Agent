# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

My-Chat-LangChain (Stream-Agent) 是一个全栈 AI 研究助理应用，基于 LangChain + LangGraph 构建，支持多工具 Agent、网络搜索、RAG 知识库、E2B 云沙箱代码执行、多模态交互等功能。

**当前版本**: V9.0 (开发中)
**开发计划**: 详见 `Note/Plan-V9.md`

## 开发环境

- **Conda 环境**: `My-Chat-LangChain`
- **Python 完整路径**: `A:/Anaconda/envs/My-Chat-LangChain/python.exe`
- **激活命令**: `conda activate My-Chat-LangChain`
- **Node.js**: v18+ (前端开发)

> **注意**: Claude Code 可使用 Python 完整路径直接执行命令，无需手动激活 conda 环境。

## 系统架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        My-Chat-LangChain V9.0                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Frontend (Next.js 14 + shadcn/ui + Tailwind)     Port: 3000            │
│                            │                                            │
│                     HTTP/REST + SSE                                     │
│                            │                                            │
│  ┌─────────────────────────┼─────────────────────────┐                  │
│  │                         │                         │                  │
│  ▼                         ▼                         ▼                  │
│  auth-service         chat-service             rag-service              │
│  (FastAPI)            (FastAPI)                (FastAPI)                │
│  Port: 8001           Port: 8002               Port: 8004               │
│  - 用户注册/登录       - 聊天流式                - 文档解析              │
│  - JWT Token          - LangGraph Agent         - 混合检索 (向量+BM25)   │
│  - 权限验证           - 工具执行 (96+)          - 引用追溯              │
│                       - 会话管理                - Reranker 重排序       │
│                            │                         │                  │
│                            ▼                         ▼                  │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                        Data Layer                                │    │
│  │  PostgreSQL (用户/会话)  │  PgvectorService (向量检索)           │    │
│  │  SQLite (本地测试)       │  BM25Service (关键词检索)             │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  External Services: Gemini | E2B Sandbox | MCP Tools | MinerU   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

## 服务端口

| 服务 | 端口 | 说明 |
|------|------|------|
| frontend-next | 3000 | Next.js 前端 |
| auth-service | 8001 | 用户认证服务 |
| chat-service | 8002 | 聊天核心服务 (LangGraph Agent) |
| whisper-service | 8003 | 语音识别服务 (可选) |
| rag-service | 8004 | RAG 检索服务 |
| presentation-service | 8005 | 演示文稿生成服务 |

## 开发命令

```bash
# 激活 Conda 环境 (必须)
conda activate My-Chat-LangChain

# ============ 后端服务 ============
# 启动 Auth 服务
cd backend/auth-service && uvicorn app.main:app --port 8001 --reload

# 启动 Chat 服务 (主后端)
cd backend/chat-service && uvicorn app.main:app --port 8002 --reload

# 启动 RAG 服务
cd backend/rag-service && uvicorn app.main:app --port 8004 --reload

# 启动 Whisper 服务 (可选)
cd backend/whisper-service && uvicorn app.main:app --port 8003 --reload

# 启动 Presentation 服务
cd backend/presentation-service && uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload

# ============ 前端 ============
cd frontend-next && npm run dev

# ============ 测试 ============
# 运行单个服务的所有测试
cd backend/rag-service && A:/Anaconda/envs/My-Chat-LangChain/python.exe -m pytest tests/ -v --tb=short
cd backend/presentation-service && A:/Anaconda/envs/My-Chat-LangChain/python.exe -m pytest tests/ -v --tb=short

# 运行单个测试文件
A:/Anaconda/envs/My-Chat-LangChain/python.exe -m pytest tests/test_theme_service.py -v --tb=short

# 运行单个测试函数
A:/Anaconda/envs/My-Chat-LangChain/python.exe -m pytest tests/test_theme_service.py::TestThemeService::test_get_theme -v

# 或手动执行
conda activate My-Chat-LangChain
cd backend/rag-service && python -m pytest tests/ -v --tb=short

# ============ Docker ============
docker-compose up -d --build
docker-compose logs -f
docker-compose down
```

## 目录结构

```
LangChain-Agent/
├── backend/
│   ├── auth-service/          # 认证微服务
│   │   └── app/
│   │       ├── api/v1/        # API 路由
│   │       ├── core/          # 安全、依赖
│   │       ├── models/        # SQLAlchemy 模型
│   │       └── schemas/       # Pydantic Schema
│   ├── chat-service/          # 聊天微服务
│   │   └── app/
│   │       ├── services/      # Agent 服务
│   │       └── tools/         # LangChain 工具
│   ├── rag-service/           # RAG 微服务
│   │   └── app/
│   │       ├── services/      # 向量/BM25/重排序服务
│   │       │   ├── pgvector_service.py   # pgvector 向量存储
│   │       │   ├── milvus_service.py     # Milvus 向量存储
│   │       │   ├── bm25_service.py       # BM25 关键词检索
│   │       │   └── search_service.py     # 混合检索
│   │       └── tests/         # 自动化测试
│   ├── presentation-service/  # 演示文稿微服务
│   │   └── app/
│   │       ├── services/      # 核心服务
│   │       │   ├── presentation_service.py  # AI 生成 PPT
│   │       │   ├── theme_service.py         # 17 种主题系统
│   │       │   ├── layout_engine.py         # 19 种布局引擎
│   │       │   ├── image_service.py         # 图片服务 (Picsum)
│   │       │   ├── export_service.py        # HTML 导出
│   │       │   └── intent_parser.py         # AI 对话式修改
│   │       └── tests/         # 172 项自动化测试
│   └── whisper-service/       # 语音识别微服务 (可选)
├── frontend-next/             # Next.js 14 前端
│   ├── src/
│   │   ├── app/               # App Router 页面
│   │   ├── components/        # React 组件
│   │   │   └── presentations/ # PPT 相关组件
│   │   │       ├── SlidePreview.tsx      # 幻灯片预览
│   │   │       └── PresentationPlayer.tsx # 演示播放器
│   │   ├── stores/            # Zustand 状态管理
│   │   └── lib/               # 工具函数、API
│   └── public/
└── Note/
    └── Plan-V9.md             # 开发计划文档
```

## 核心模块

| 模块 | 文件 | 职责 |
|------|------|------|
| **认证** | `auth-service/app/` | JWT 认证、用户管理 |
| **聊天** | `chat-service/app/services/` | LangGraph Agent、流式响应 |
| **RAG** | `rag-service/app/services/` | 混合检索、文档解析、引用追溯 |
| **向量存储** | `pgvector_service.py` | PostgreSQL + pgvector / SQLite (测试) |
| **演示文稿** | `presentation-service/app/services/` | AI 生成 PPT、主题、布局、导出 |
| **前端** | `frontend-next/src/` | Next.js 14 + shadcn/ui |

## 环境变量

**backend/.env** (各服务共享或单独配置):
```bash
# LLM
GOOGLE_API_KEY=xxx              # Gemini API (必需)

# 数据库
DATABASE_URL=postgresql://...   # PostgreSQL (生产)
# DATABASE_URL=sqlite:///./test.db  # SQLite (测试)

# 向量存储
VECTOR_STORE_BACKEND=pgvector   # pgvector 或 milvus
PGVECTOR_ENABLED=true

# 外部服务
E2B_API_KEY=xxx                 # E2B 代码执行
SERPER_API_KEY=xxx              # 搜索 API
BRIGHT_DATA_API_KEY=xxx         # BrightData MCP

# JWT
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
```

## 工具系统

项目包含 96+ 工具，分为三类：
1. **MCP 工具** (~90): 网络搜索、电商数据、社交媒体、学术论文等
2. **自定义工具** (4): RAG 摄取/查询、论文格式化
3. **E2B 工具** (6): Python 代码执行、CSV 分析等

## 技术栈

| 层级 | 技术 |
|------|------|
| **前端** | Next.js 14, React 18, TypeScript, shadcn/ui, Tailwind CSS, Zustand |
| **后端** | FastAPI, Uvicorn, Pydantic, SQLAlchemy |
| **Agent** | LangGraph, LangChain, MCP Adapters |
| **向量数据库** | PgvectorService (PostgreSQL + pgvector) / SQLite (测试) |
| **LLM** | Google Gemini (主) / OpenAI 兼容 |
| **部署** | Render (计算) + Supabase (数据库 + pgvector) |

## 开发规范

### Claude Code 自动化开发流程 (必须遵循)

**每完成一个小模块，必须按以下顺序执行：**

1. **获取文档** (必要时)
   - 使用 Context7 MCP 工具获取相关库/框架的最新文档
   - 示例: `mcp__upstash-context7-mcp__resolve-library-id` + `mcp__upstash-context7-mcp__get-library-docs`

2. **编写代码**
   - 编写功能代码和对应的测试用例
   - 遵循代码风格规范

3. **自动测试**
   - 运行 pytest 测试，确保所有测试通过
   - 测试命令: `A:/Anaconda/envs/My-Chat-LangChain/python.exe -m pytest tests/test_xxx.py -v --tb=short`

4. **更新 .gitignore**
   - 检查是否有新的需要忽略的文件类型
   - 根据项目结构实时更新 `.gitignore`

5. **自动提交代码**
   - 生成详细的中文版 Git 提交信息
   - 格式: `<type>(<scope>): <简短描述>\n\n<详细说明>`
   - 自动执行 `git add` 和 `git commit`

6. **更新开发文档**
   - 更新 `Note/Plan-V9.md` 中对应任务的状态
   - 标记完成项: `- [x] 任务名称 ✅ 测试通过`
   - 添加变更记录到文档末尾的变更历史

7. **提交文档更新**
   - 单独提交文档更新: `docs(plan): 更新 xxx 完成状态`

### Git 提交规范
- 使用中文提交信息
- 格式: `<type>(<scope>): <description>`
- 类型: feat / fix / docs / refactor / test / chore
- 提交信息末尾添加:
  ```
  🤖 Generated with [Claude Code](https://claude.com/claude-code)

  Co-Authored-By: Claude <noreply@anthropic.com>
  ```

### 代码风格
- 使用中文注释和文档字符串
- 遵循 PEP 8 规范
- 类型注解必须完整

### 开发协作流程
1. Claude 编写代码和测试脚本
2. Claude 自动运行测试 (使用完整 Python 路径)
3. 测试通过后 Claude 自动提交代码
4. Claude 更新开发文档并提交
5. 如有测试失败，修复后重复步骤 2-4

## API 文档

各服务启动后访问:
- Auth: http://localhost:8001/docs
- Chat: http://localhost:8002/docs
- RAG: http://localhost:8004/docs

## 参考文档

- 开发计划: `Note/Plan-V9.md`
- 部署方案: Plan-V9.md 第八章 (Render + Supabase)

## 常见问题与解决方案

### 前后端联调问题

#### 问题 1: 浏览器代理拦截本地请求

**症状**: 前端无法连接后端服务，curl 返回 `502 Bad Gateway`

**原因**: 系统代理软件 (如 Clash Verge) 拦截了发往 `127.0.0.1` 的请求

**解决方案**:
1. **Next.js rewrites 代理** (推荐): 在 `next.config.ts` 中配置 rewrites，让 Next.js 服务端转发请求
   ```typescript
   async rewrites() {
     return [
       {
         source: "/api/v1/:path*",
         destination: "http://127.0.0.1:8005/api/v1/:path*",
       },
     ];
   }
   ```
2. **前端 API 客户端使用相对路径**: `baseURL: ''` 而不是 `http://127.0.0.1:8005`

#### 问题 2: 端口被旧进程占用

**症状**: 服务启动成功但请求超时，端口显示 OPEN 但 HTTP 无响应

**诊断命令**:
```bash
netstat -ano | findstr ":8005" | findstr "LISTENING"
```

**原因**: 旧的 Python 进程没有完全关闭，在同一端口上监听但不处理请求

**解决方案**:
```bash
# 1. 查找占用端口的进程
netstat -ano | findstr ":8005" | findstr "LISTENING"

# 2. 查看进程详情
powershell -Command "Get-Process -Id <PID> | Select-Object Id, ProcessName, Path"

# 3. 杀掉旧进程
powershell -Command "Stop-Process -Id <PID> -Force"

# 4. 重启服务 (使用 0.0.0.0 绑定)
uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload
```

#### 问题 3: 测试后端连通性

**使用 Python 绕过代理测试**:
```python
import urllib.request

no_proxy_handler = urllib.request.ProxyHandler({})
opener = urllib.request.build_opener(no_proxy_handler)

req = urllib.request.Request('http://127.0.0.1:8005/health')
response = opener.open(req, timeout=5)
print(f'Status: {response.status}')
print(f'Response: {response.read().decode()}')
```

### 服务启动注意事项

1. **presentation-service 必须使用 `--host 0.0.0.0`**: 避免只绑定 `127.0.0.1` 导致的连接问题
2. **启动服务前检查端口占用**: 使用 `netstat -ano | findstr ":<PORT>"` 检查
3. **重启服务时先杀掉旧进程**: 避免端口冲突
