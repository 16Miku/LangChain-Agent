# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

My-Chat-LangChain (Stream-Agent) 是一个全栈 AI 研究助理应用，基于 LangChain + LangGraph 构建，支持多工具 Agent、网络搜索、RAG 知识库、E2B 云沙箱代码执行、多模态交互等功能。

**当前版本**: V9.0 (开发中)
**开发计划**: 详见 `Note/Plan-V9.md`

## 开发环境

- **Conda 环境**: `My-Chat-LangChain`
- **Python 路径**: `A:/Anaconda/envs/My-Chat-LangChain/python.exe`
- **激活命令**: `conda activate My-Chat-LangChain`
- **Node.js**: v18+ (前端开发)

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

# ============ 前端 ============
cd frontend-next && npm run dev

# ============ 测试 ============
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
│   └── whisper-service/       # 语音识别微服务 (可选)
├── frontend-next/             # Next.js 14 前端
│   ├── src/
│   │   ├── app/               # App Router 页面
│   │   ├── components/        # React 组件
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

### Git 提交规范
- 使用中文提交信息
- 格式: `<type>(<scope>): <description>`
- 类型: feat / fix / docs / refactor / test / chore

### 代码风格
- 使用中文注释和文档字符串
- 遵循 PEP 8 规范
- 类型注解必须完整

### 开发协作流程
1. Claude 编写代码和测试脚本
2. 用户在 conda 环境中运行测试
3. 用户反馈测试结果
4. 修复问题（如有）
5. 用户手动 git commit
6. 更新 `Note/Plan-V9.md` 开发进度

## API 文档

各服务启动后访问:
- Auth: http://localhost:8001/docs
- Chat: http://localhost:8002/docs
- RAG: http://localhost:8004/docs

## 参考文档

- 开发计划: `Note/Plan-V9.md`
- 部署方案: Plan-V9.md 第八章 (Render + Supabase)
