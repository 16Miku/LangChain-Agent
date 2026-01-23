# My-Chat-LangChain V9.0 系统说明文档

> **版本**: V9.0
> **文档日期**: 2026-01-23
> **项目状态**: 生产就绪 (Phase 5 开发中)
> **作者**: Claude Code

---

## 📑 文档目录

1. [项目概述](#一项目概述)
2. [系统架构](#二系统架构)
3. [核心功能模块](#三核心功能模块)
4. [后端服务详解](#四后端服务详解)
5. [前端架构详解](#五前端架构详解)
6. [开发环境配置](#六开发环境配置)
7. [部署指南](#七部署指南)
8. [代码阅读指南](#八代码阅读指南)
9. [API 接口文档](#九api-接口文档)
10. [数据库设计](#十数据库设计)
11. [工具系统说明](#十一工具系统说明)
12. [常见问题与解决方案](#十二常见问题与解决方案)
13. [更新日志](#十三更新日志)

---

## 一、项目概述

### 1.1 项目简介

**My-Chat-LangChain** (代号 Stream-Agent) 是一个全栈 AI 研究助理应用，基于 LangChain + LangGraph 构建，支持多工具 Agent、网络搜索、RAG 知识库、E2B 云沙箱代码执行、多模态交互等功能。

**V9.0 版本核心特性**：
- 🎨 现代化前端 (Next.js 14 + shadcn/ui)
- 🔐 完整用户认证系统 (JWT)
- 🖼️ 多模态交互 (图片理解 + 语音交互)
- 📚 RAG 增强检索 (向量 + BM25 + 重排序)
- 🎤 AI 生成演示文稿 (Presentation Service)
- ☁️ 云端部署支持 (Render + Supabase)

### 1.2 技术栈总览

| 层级 | 技术选型 | 版本/说明 |
|------|---------|----------|
| **前端框架** | Next.js | 14.x (App Router) |
| **UI 组件库** | shadcn/ui | 基于 Radix UI |
| **CSS 框架** | Tailwind CSS | 4.0 |
| **状态管理** | Zustand | 4.x |
| **后端框架** | FastAPI | 0.115+ |
| **Agent 框架** | LangGraph | 最新版 |
| **向量存储** | Pgvector (PostgreSQL) / SQLite (测试) |
| **关系数据库** | PostgreSQL / SQLite |
| **语言模型** | Google Gemini (主) / OpenAI 兼容 |
| **代码执行** | E2B Sandbox |
| **语音服务** | faster-whisper + edge-tts |
| **部署平台** | Render + Supabase |

### 1.3 服务端口清单

| 服务名称 | 端口 | 协议 | 说明 |
|---------|------|------|------|
| frontend-next | 3000 | HTTP | Next.js 前端应用 |
| auth-service | 8001 | HTTP | 用户认证服务 |
| chat-service | 8002 | HTTP | 聊天核心服务 (LangGraph Agent) |
| whisper-service | 8003 | HTTP | 语音识别服务 |
| rag-service | 8004 | HTTP | RAG 检索服务 |
| presentation-service | 8005 | HTTP | 演示文稿生成服务 |

### 1.4 项目结构

```
LangChain-Agent/
├── backend/                          # 后端服务目录
│   ├── auth-service/                 # 认证微服务 (端口 8001)
│   │   └── app/
│   │       ├── api/v1/               # API 路由
│   │       │   ├── auth.py           # 认证接口 (注册/登录/刷新)
│   │       │   └── users.py          # 用户接口
│   │       ├── core/                 # 核心模块
│   │       │   ├── config.py         # 配置管理
│   │       │   ├── security.py       # JWT/密码加密
│   │       │   └── deps.py           # 依赖注入
│   │       ├── models/               # SQLAlchemy 模型
│   │       │   └── user.py           # 用户数据模型
│   │       ├── schemas/              # Pydantic Schema
│   │       │   ├── user.py           # 用户 Schema
│   │       │   └── token.py          # Token Schema
│   │       ├── services/             # 业务逻辑
│   │       │   └── user_service.py   # 用户服务
│   │       ├── database.py           # 数据库连接
│   │       └── main.py               # FastAPI 应用入口
│   │
│   ├── chat-service/                 # 聊天微服务 (端口 8002)
│   │   └── app/
│   │       ├── api/v1/               # API 路由
│   │       │   ├── chat.py           # 聊天接口 (流式/SSE)
│   │       │   ├── conversation.py   # 会话管理
│   │       │   └── upload.py         # 文件上传
│   │       ├── services/             # 业务逻辑
│   │       │   ├── agent_service.py  # LangGraph Agent 核心
│   │       │   └── llm_service.py    # LLM 调用封装
│   │       ├── tools/                # LangChain 工具集
│   │       │   ├── e2b_tools.py      # E2B 代码执行工具
│   │       │   ├── search_tools.py   # 搜索工具
│   │       │   ├── mcp_tools.py      # MCP 工具适配器
│   │       │   └── presentation_tools.py  # PPT 生成工具
│   │       ├── models/               # 数据模型
│   │       │   ├── conversation.py   # 会话模型
│   │       │   └── message.py        # 消息模型
│   │       └── main.py               # FastAPI 应用入口
│   │
│   ├── rag-service/                  # RAG 检索微服务 (端口 8004)
│   │   └── app/
│   │       ├── api/v1/               # API 路由
│   │       │   ├── documents.py      # 文档管理
│   │       │   ├── search.py         # 检索接口
│   │       │   └── ingest.py         # 文档摄取
│   │       ├── services/             # 核心服务
│   │       │   ├── pgvector_service.py   # Pgvector 向量存储
│   │       │   ├── milvus_service.py     # Milvus 向量存储 (备用)
│   │       │   ├── bm25_service.py       # BM25 关键词检索
│   │       │   ├── search_service.py     # 混合检索服务
│   │       │   ├── rerank_service.py     # 重排序服务
│   │       │   ├── chunking_service.py   # 智能分块服务
│   │       │   └── citation_service.py   # 引用追溯服务
│   │       ├── models/               # 数据模型
│   │       │   ├── document.py       # 文档模型
│   │       │   └── chunk.py          # 分块模型
│   │       └── main.py               # FastAPI 应用入口
│   │
│   ├── whisper-service/              # 语音服务 (端口 8003)
│   │   └── app/
│   │       ├── api/v1/
│   │       │   └── transcribe.py     # 语音转文字
│   │       ├── services/
│   │       │   ├── whisper_service.py    # Whisper 识别
│   │       │   └── tts_service.py        # TTS 合成
│   │       └── main.py
│   │
│   ├── presentation-service/         # 演示文稿服务 (端口 8005)
│   │   └── app/
│   │       ├── api/v1/
│   │       │   ├── presentations.py  # CRUD API
│   │       │   ├── editor.py         # 编辑器 API
│   │       │   └── export.py         # 导出 API
│   │       ├── services/             # 核心服务
│   │       │   ├── presentation_service.py  # AI 生成 PPT
│   │       │   ├── layout_engine.py         # 19 种布局引擎
│   │       │   ├── theme_service.py          # 17 种主题系统
│   │       │   ├── image_service.py          # 图片服务 (Picsum)
│   │       │   ├── export_service.py         # HTML 导出
│   │       │   ├── pptx_export_service.py    # PPTX 导出
│   │       │   └── intent_parser.py          # AI 对话式修改
│   │       ├── models/               # 数据模型
│   │       │   ├── presentation.py   # 演示文稿模型
│   │       │   └── slide_version.py   # 幻灯片版本模型
│   │       └── main.py
│   │
│   └── .env                          # 环境变量配置
│
├── frontend-next/                    # Next.js 14 前端
│   ├── src/
│   │   ├── app/                      # App Router 页面
│   │   │   ├── (auth)/               # 认证路由组
│   │   │   │   ├── login/
│   │   │   │   └── register/
│   │   │   ├── (main)/               # 主应用路由组
│   │   │   │   ├── chat/             # 聊天页面
│   │   │   │   ├── documents/        # 文档管理页面
│   │   │   │   ├── presentations/    # 演示文稿页面
│   │   │   │   └── settings/         # 设置页面
│   │   │   ├── layout.tsx            # 根布局
│   │   │   ├── page.tsx              # 首页
│   │   │   └── globals.css           # 全局样式
│   │   │
│   │   ├── components/               # React 组件
│   │   │   ├── chat/                 # 聊天组件
│   │   │   │   ├── ChatContainer.tsx
│   │   │   │   ├── MessageList.tsx
│   │   │   │   ├── MessageBubble.tsx
│   │   │   │   ├── InputArea.tsx
│   │   │   │   ├── ToolCallPanel.tsx
│   │   │   │   └── CodeBlock.tsx
│   │   │   ├── sidebar/              # 侧边栏组件
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   ├── ConversationList.tsx
│   │   │   │   └── ConversationItem.tsx
│   │   │   ├── presentations/        # 演示文稿组件
│   │   │   │   ├── PresentationListPage.tsx
│   │   │   │   ├── PresentationEditorPage.tsx
│   │   │   │   ├── SlideEditor.tsx
│   │   │   │   ├── SlidePreview.tsx
│   │   │   │   └── ThemeSelector.tsx
│   │   │   ├── documents/            # 文档管理组件
│   │   │   │   └── DocumentsPage.tsx
│   │   │   ├── voice/                # 语音组件
│   │   │   │   ├── VoiceRecorder.tsx
│   │   │   │   └── AudioPlayer.tsx
│   │   │   └── providers/            # Context Provider
│   │   │       ├── AuthProvider.tsx
│   │   │       └── ThemeProvider.tsx
│   │   │
│   │   ├── lib/                      # 工具库
│   │   │   ├── api/                  # API 客户端
│   │   │   │   ├── client.ts         # Axios 实例
│   │   │   │   ├── auth.ts           # 认证 API
│   │   │   │   ├── chat.ts           # 聊天 API
│   │   │   │   ├── rag.ts            # RAG API
│   │   │   │   ├── voice.ts          # 语音 API
│   │   │   │   └── presentations.ts  # 演示文稿 API
│   │   │   ├── stores/               # Zustand 状态管理
│   │   │   │   ├── authStore.ts      # 认证状态
│   │   │   │   ├── chatStore.ts      # 聊天状态
│   │   │   │   ├── settingsStore.ts  # 设置状态
│   │   │   │   └── presentationStore.ts  # 演示文稿状态
│   │   │   ├── types/                # TypeScript 类型
│   │   │   │   ├── auth.ts
│   │   │   │   ├── chat.ts
│   │   │   │   └── presentations.ts
│   │   │   └── utils/                # 工具函数
│   │   │       ├── markdown.ts       # Markdown 处理
│   │   │       └── format.ts         # 格式化工具
│   │   │
│   │   └── hooks/                    # React Hooks
│   │       ├── useSSE.ts             # SSE 流式处理
│   │       ├── useDebounce.ts        # 防抖 Hook
│   │       └── index.ts
│   │
│   ├── public/                       # 静态资源
│   ├── tailwind.config.ts            # Tailwind 配置
│   ├── next.config.ts                # Next.js 配置
│   └── package.json
│
├── database/                         # 数据库相关
│   ├── supabase_schema.sql           # Supabase 数据库结构
│   └── migrations/                   # 数据库迁移文件
│
├── docs/                             # 文档目录
│   └── deploy-render.md              # Render 部署指南
│
├── Note/                             # 项目笔记
│   └── Plan-V9.md                    # V9 开发计划
│
├── .env.example                      # 环境变量模板
├── .gitignore                        # Git 忽略文件
├── docker-compose.yml                # Docker Compose 配置
└── README.md                         # 项目说明
```

### 1.5 核心功能特性

#### 1.5.1 AI 对话功能
- 基于 LangGraph 的智能 Agent 架构
- 支持流式响应 (SSE)
- 96+ 内置工具 (搜索、代码执行、数据分析等)
- 上下文记忆与多轮对话
- 工具调用可视化展示

#### 1.5.2 用户认证系统
- JWT Token 认证
- 用户注册/登录/登出
- Token 自动刷新
- 会话管理与隔离
- 个人设置持久化

#### 1.5.3 多模态交互
- **图片理解**: 支持上传图片进行 AI 分析
- **OCR 识别**: 图片文字提取 (规划中)
- **语音输入**: Whisper 语音转文字
- **语音输出**: Edge TTS 文字转语音

#### 1.5.4 RAG 知识库
- 混合检索 (向量相似度 + BM25 关键词)
- RRF (Reciprocal Rank Fusion) 融合算法
- 智能分块 (语义/页面感知/递归)
- 引用追溯与来源标注
- Reranker 重排序

#### 1.5.5 演示文稿生成
- AI 自动生成 PPT 大纲
- 19 种专业布局类型
- 17 种精品主题
- 在线编辑器 (实时编辑/拖拽)
- 导出 HTML / PPTX
- AI 对话式修改

### 1.6 开发进度总览

| 阶段 | 名称 | 状态 | 完成度 |
|------|------|------|--------|
| Phase 1 | 前端重构 + 用户系统 | ✅ 已完成 | 100% |
| Phase 2 | 多模态能力 | ✅ 已完成 | 100% |
| Phase 3 | RAG 增强 | ✅ 已完成 | 100% |
| Phase 4 | 部署优化 | ✅ 已完成 | 100% |
| Phase 5 | AI 生成 PPT | 🚧 进行中 | ~75% |

**总体进度**: 149/199 任务完成 (75%)

---

## 二、系统架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           My-Chat-LangChain V9.0                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Frontend Layer (Next.js 14)                      │   │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────────────┐    │   │
│  │  │ Chat Page │ │Login/Reg  │ │ Documents  │ │ Presentations     │    │   │
│  │  │           │ │           │ │   Page    │ │     Page          │    │   │
│  │  └───────────┘ └───────────┘ └───────────┘ └───────────────────┘    │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │                    shadcn/ui + Tailwind                      │    │   │
│  │  │              + Zustand State Management                      │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                          HTTP/REST + SSE (Server-Sent Events)            │
│                                    │                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        API Layer (Optional)                          │   │
│  │                    Nginx Reverse Proxy / Load Balancer              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│          ┌─────────────────────────┼─────────────────────────┐              │
│          │                         │                         │              │
│          ▼                         ▼                         ▼              │
│  ┌───────────────┐        ┌───────────────┐        ┌───────────────┐       │
│  │  Auth Service │        │  Chat Service │        │  RAG Service  │       │
│  │  (FastAPI)    │        │  (FastAPI)    │        │  (FastAPI)    │       │
│  │  Port: 8001   │        │  Port: 8002   │        │  Port: 8004   │       │
│  │               │        │               │        │               │       │
│  │ - JWT Auth    │        │ - LangGraph   │        │ - Pgvector    │       │
│  │ - User Mgmt   │        │ - Agent Tools │        │ - BM25 Search │       │
│  │ - Token Refresh│       │ - Stream SSE  │        │ - Reranker    │       │
│  └───────┬───────┘        └───────┬───────┘        └───────┬───────┘       │
│          │                         │                         │              │
│          ▼                         ▼                         ▼              │
│  ┌───────────────┐        ┌───────────────┐        ┌───────────────┐       │
│  │ Whisper Svc   │        │ Presentation │        │   External    │       │
│  │  (FastAPI)    │        │    Service    │        │   Services    │       │
│  │  Port: 8003   │        │  Port: 8005   │        │               │       │
│  │               │        │               │        │ ┌───────────┐ │       │
│  │ - Whisper STT │        │ - AI PPT Gen  │        │ │ Gemini    │ │       │
│  │ - Edge TTS    │        │ - 19 Layouts  │        │ │ E2B       │ │       │
│  │               │        │ - 17 Themes   │        │ │ MCP Tools │ │       │
│  └───────────────┘        └───────────────┘        │ │ Search API│ │       │
│                                                     └───────────┘ │       │
│  ┌───────────────────────────────────────────────────────────────────┐     │
│  │                         Data Layer                                 │     │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────┐ │     │
│  │  │ PostgreSQL  │  │   Pgvector  │  │    SQLite   │  │  Local   │ │     │
│  │  │ - users     │  │ - embeddings│  │ - test mode │  │  Files   │ │     │
│  │  │ - sessions  │  │ - documents │  │             │  │          │ │     │
│  │  │ - messages  │  │             │  │             │  └──────────┘ │     │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                │     │
│  └───────────────────────────────────────────────────────────────────┘     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 服务间通信

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          服务通信架构图                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌───────────┐                                                             │
│   │  Browser  │                                                             │
│   └─────┬─────┘                                                             │
│         │                                                                    │
│         │ HTTP + SSE                                                         │
│         │                                                                    │
│         ▼                                                                    │
│   ┌───────────────────────────────────────┐                                  │
│   │         Next.js Frontend              │                                  │
│   │         (Port: 3000)                  │                                  │
│   └───────────────┬───────────────────────┘                                  │
│                   │                                                            │
│         ┌─────────┼─────────┐                                                │
│         │         │         │                                                │
│         ▼         ▼         ▼                                                │
│   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌──────────┐             │
│   │   Auth  │ │  Chat   │ │   RAG   │ │ Whisper │ │Present.  │             │
│   │ :8001   │ │ :8002   │ │ :8004   │ │ :8003   │ │  :8005   │             │
│   └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬─────┘             │
│        │           │           │           │           │                   │
│        ▼           ▼           ▼           ▼           ▼                   │
│   ┌─────────────────────────────────────────────────────────────────┐    │
│   │                      PostgreSQL / SQLite                        │    │
│   │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐            │    │
│   │  │  users  │  │sessions │  │ messages │  │documents│            │    │
│   │  └─────────┘  └─────────┘  └─────────┘  └─────────┘            │    │
│   └─────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 数据流向图

#### 2.3.1 用户聊天流程

```
用户输入消息
     │
     ▼
┌─────────────────┐
│  Frontend       │
│  - MessageBubble │
│  - InputArea     │
└────────┬────────┘
         │ POST /api/chat/stream
         │ (with JWT Token)
         ▼
┌─────────────────┐
│  Chat Service   │
│  - 验证 Token    │
│  - 获取会话上下文│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LangGraph Agent│
│  - 解析用户意图  │
│  - 决策调用工具  │
└────────┬────────┘
         │
    ┌────┴────┬─────────┬────────────┐
    │         │         │            │
    ▼         ▼         ▼            ▼
┌──────┐ ┌──────┐ ┌──────┐    ┌──────────┐
│ RAG  │ │Search│ │ E2B  │    │ Other    │
│ API  │ │ API  │ │ API  │    │ Tools    │
└──┬───┘ └──┬───┘ └──┬───┘    └────┬─────┘
   │        │        │             │
   └────────┴────────┴─────────────┘
                    │
                    ▼
            ┌───────────────┐
            │  LLM Response  │
            │  (Streaming)   │
            └───────┬────────┘
                    │ SSE Events
                    ▼
            ┌───────────────┐
            │   Frontend    │
            │  - 实时显示    │
            │  - 工具可视化  │
            └───────────────┘
```

#### 2.3.2 RAG 检索流程

```
用户上传文档
     │
     ▼
┌─────────────────┐
│  Document Page  │
│  - 选择文件      │
└────────┬────────┘
         │ POST /api/documents/upload
         ▼
┌─────────────────┐
│   RAG Service   │
│  - 接收文件      │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌────────────┐
│ Extract│ │ Chunking   │
│  Text  │ │  Service   │
└───┬────┘ └─────┬──────┘
    │            │
    ▼            ▼
┌────────┐ ┌────────────┐
│Embedding│ │ Store to DB │
│ API    │ └────────────┘
└───┬────┘
    │
    ▼
┌────────────┐
│  Pgvector  │
│  Storage   │
└────────────┘

[用户提问时]
     │
     ▼
┌─────────────────┐
│  Query          │
│  - 向量检索      │
│  - BM25 检索     │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌────────┐
│ Vector │ │ BM25   │
│Search  │ │ Search │
└───┬────┘ └───┬────┘
    │           │
    └─────┬─────┘
          │ RRF Fusion
          ▼
    ┌──────────┐
    │ Reranker │
    └─────┬────┘
          │
          ▼
    ┌──────────┐
    │  Results │
    │ + Citations│
    └──────────┘
```

### 2.4 技术架构分层

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              表现层 (Presentation)                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Next.js 14 + shadcn/ui + Tailwind CSS                                │   │
│  │  - React Server Components                                           │   │
│  │  - App Router (File-based routing)                                    │   │
│  │  - Zustand (Client-side state)                                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────────┤
│                              应用层 (Application)                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  FastAPI Microservices                                               │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────────────┐    │   │
│  │  │ Auth Svc    │ │ Chat Svc    │ │ RAG Svc     │ │ Present. Svc │    │   │
│  │  │ - JWT       │ │ - LangGraph │ │ - Hybrid    │ │ - AI PPT Gen │    │   │
│  │  │ - Users     │ │ - Tools     │ │ - Reranker  │ │ - 19 Layouts │    │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └──────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────────┤
│                              业务层 (Business)                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  LangGraph Agent + LangChain Tools                                  │   │
│  │  ┌───────────────────────────────────────────────────────────────┐  │   │
│  │  │  Agent State Machine                                            │  │   │
│  │  │  - Intent Classification                                        │  │   │
│  │  │  - Tool Selection                                               │  │   │
│  │  │  - Response Generation                                          │  │   │
│  │  └───────────────────────────────────────────────────────────────┘  │   │
│  │  ┌───────────────────────────────────────────────────────────────┐  │   │
│  │  │  Tool Ecosystem (96+ tools)                                    │  │   │
│  │  │  - MCP Tools (90): Search, E-commerce, Social, Academic       │  │   │
│  │  │  - Custom Tools (4): RAG, Citation                             │  │   │
│  │  │  - E2B Tools (6): Python execution, CSV analysis              │  │   │
│  │  └───────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────────┤
│                              数据层 (Data)                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Data Storage                                                        │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │ PostgreSQL   │  │ Pgvector     │  │ SQLite       │              │   │
│  │  │ - Users      │  │ - Embeddings │  │ - Test mode  │              │   │
│  │  │ - Sessions   │  │ - Chunks     │  │              │              │   │
│  │  │ - Messages   │  │              │  │              │              │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────────┤
│                            外部服务层 (External)                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Third-party APIs                                                    │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────┐    │   │
│  │  │ Gemini  │ │   E2B   │ │  MCP    │ │ Whisper │ │ Edge TTS    │    │   │
│  │  │ Vision  │ │ Sandbox │ │ Tools   │ │ (Local) │ │  (Local)    │    │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.5 部署架构

#### 2.5.1 本地开发架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         本地开发环境                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  开发机 (Windows/Mac/Linux)                                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Conda Environment: My-Chat-LangChain                                  │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐ │   │
│  │  │  Python Services (uvicorn)                                       │ │   │
│  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │ │   │
│  │  │  │   Auth   │ │  Chat    │ │   RAG    │ │ Present. │           │ │   │
│  │  │  │ :8001    │ │ :8002    │ │ :8004    │ │ :8005    │           │ │   │
│  │  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │ │   │
│  │  └─────────────────────────────────────────────────────────────────┘ │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐ │   │
│  │  │  Frontend (npm run dev)                                          │ │   │
│  │  │  ┌──────────────────────────────────────────────────────────┐  │ │   │
│  │  │  │  Next.js Dev Server                                       │  │ │   │
│  │  │  │  http://localhost:3000                                   │  │ │   │
│  │  │  └──────────────────────────────────────────────────────────┘  │ │   │
│  │  └─────────────────────────────────────────────────────────────────┘ │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐ │   │
│  │  │  Databases                                                       │ │   │
│  │  │  ┌──────────────┐  ┌──────────────┐                             │ │   │
│  │  │  │ SQLite       │  │ Local Files  │                             │ │   │
│  │  │  │ (test mode)  │  │ (uploads)    │                             │ │   │
│  │  │  └──────────────┘  └──────────────┘                             │ │   │
│  │  └─────────────────────────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 2.5.2 云端部署架构 (Render + Supabase)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Render + Supabase 云部署架构                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         Render (计算层)                               │   │
│  │  ┌───────────────────────────────────────────────────────────────┐  │   │
│  │  │  Web Services (5个独立服务)                                    │  │   │
│  │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │  │   │
│  │  │  │ frontend-next│  │ auth-service │  │ chat-service │         │  │   │
│  │  │  │   (Static)   │  │   (API)      │  │   (API)      │         │  │   │
│  │  │  └──────────────┘  └──────────────┘  └──────────────┘         │  │   │
│  │  │  ┌──────────────┐  ┌──────────────┐                         │  │   │
│  │  │  │  rag-service │  │present.service│                         │  │   │
│  │  │  │   (API)      │  │   (API)      │                         │  │   │
│  │  │  └──────────────┘  └──────────────┘                         │  │   │
│  │  └───────────────────────────────────────────────────────────────┘  │   │
│  │                          │                                         │   │
│  └──────────────────────────┼─────────────────────────────────────────┘   │
│                             │                                             │
│                             ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Supabase (数据层)                               │   │
│  │  ┌───────────────────────────────────────────────────────────────┐  │   │
│  │  │  PostgreSQL Database                                            │  │   │
│  │  │  - pgvector Extension (向量搜索)                                │  │   │
│  │  │  - Tables: users, sessions, messages, documents, chunks      │  │   │
│  │  │  - Row Level Security (用户隔离)                                │  │   │
│  │  └───────────────────────────────────────────────────────────────┘  │   │
│  │  ┌───────────────────────────────────────────────────────────────┐  │   │
│  │  │  Supabase Storage (可选)                                       │  │   │
│  │  │  - 文件上传/存储                                                │  │   │
│  │  └───────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  用户访问: https://<app-name>.onrender.com                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.6 安全架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              安全层设计                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  前端安全                                                               │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐ │   │
│  │  │  - 路由保护 (未登录重定向到登录页)                                 │ │   │
│  │  │  - Token 存储                                                      │ │   │
│  │  │  - XSS 防护 (React 自动转义)                                     │ │   │
│  │  │  - CSRF Token (API 请求验证)                                      │ │   │
│  │  └─────────────────────────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┘   │
│  │  传输层安全                                                             │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐ │   │
│  │  │  - HTTPS (生产环境)                                              │ │   │
│  │  │  - JWT Token (Header: Authorization: Bearer <token>)             │ │   │
│  │  │  - Refresh Token (自动刷新机制)                                   │ │   │
│  │  └─────────────────────────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┘   │
│  │  后端安全                                                               │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐ │   │
│  │  │  - Token 验证 (依赖注入: get_current_user)                       │ │   │
│  │  │  - 密码加密 (bcrypt + salt)                                       │ │   │
│  │  │  - SQL 注入防护 (SQLAlchemy ORM)                                │ │   │
│  │  │  - 用户隔离 (基于 user_id 的数据隔离)                            │ │   │
│  │  └─────────────────────────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┘   │
│  │  数据安全                                                               │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐ │   │
│  │  │  - Row Level Security (Supabase RLS)                             │ │   │
│  │  │  - 敏感信息加密 (API Keys)                                        │ │   │
│  │  │  - 会话隔离 (每个用户只能访问自己的数据)                          │ │   │
│  │  └─────────────────────────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 三、核心功能模块

### 3.1 AI 对话系统

#### 3.1.1 功能概述

AI 对话系统是整个应用的核心，基于 LangGraph 构建了智能 Agent 架构，支持多轮对话、工具调用、上下文记忆等高级功能。

#### 3.1.2 LangGraph Agent 状态机

```python
# Agent 状态定义
class AgentState(TypedDict):
    messages: List[BaseMessage]      # 消息历史
    user_id: str                     # 用户 ID
    conversation_id: str             # 会话 ID
    tool_calls: List[ToolCall]       # 工具调用记录
    next_action: str                 # 下一步动作

# 状态转换流程
START → intent_classification → tool_execution → response_generation → END
                                    ↓
                              tool_error_handling
```

**状态节点说明**:

| 节点 | 功能 | 输入 | 输出 |
|------|------|------|------|
| `intent_classification` | 意图识别 | 用户消息 | 动作类型 |
| `tool_execution` | 工具执行 | 工具名称+参数 | 执行结果 |
| `response_generation` | 生成回复 | LLM + 上下文 | 流式响应 |
| `tool_error_handling` | 错误处理 | 异常信息 | 友好提示 |

#### 3.1.3 工具调用流程

```
用户消息 "帮我搜索最新的 AI 论文"
     │
     ▼
┌─────────────────┐
│  Intent Classifier│
│  - 识别需要搜索   │
│  - 提取关键词     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Tool Selector  │
│  - 选择 search_  │
│    academic tool │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Tool Executor  │
│  - 调用 MCP API  │
│  - 获取结果      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Response Gen   │
│  - 总结结果      │
│  - 添加引用      │
└────────┬────────┘
         │
         ▼
    用户界面显示
```

#### 3.1.4 流式响应机制

**SSE (Server-Sent Events) 事件类型**:

| 事件类型 | 数据格式 | 说明 |
|---------|---------|------|
| `text` | `{content: "...", delta: true}` | 文本片段 |
| `tool_start` | `{tool_name: "...", tool_id: "..."}` | 工具开始 |
| `tool_end` | `{tool_id: "...", output: "...", duration: 1.5}` | 工具结束 |
| `citation` | `{source: "...", page: 5, content: "..."}` | 引用来源 |
| `error` | `{message: "..."}` | 错误信息 |
| `done` | `{message_id: "...", total_tokens: 1500}` | 完成 |

**前端 SSE 处理** (`useSSE.ts`):

```typescript
function useSSE(url: string, options: SSEOptions) {
  const [data, setData] = useState<SSEEvent | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const eventSource = new EventSource(url, {
      withCredentials: true
    });

    eventSource.onmessage = (event) => {
      const parsed = JSON.parse(event.data);
      setData(parsed);
    };

    eventSource.onerror = (error) => {
      console.error('SSE error:', error);
      eventSource.close();
    };

    setIsConnected(true);
    return () => eventSource.close();
  }, [url]);

  return { data, isConnected };
}
```

### 3.2 用户认证系统

#### 3.2.1 JWT 认证流程

```
用户登录
     │
     ▼
POST /api/auth/login
{username, password}
     │
     ▼
┌─────────────────┐
│  验证用户凭据    │
│  - 查询数据库    │
│  - bcrypt 验证   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  生成 JWT Token  │
│  - Access Token │
│    (15分钟)     │
│  - Refresh Token│
│    (7天)        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  返回给前端      │
│  - 存储在 localStorage │
│  - Axios 拦截器自动携带 │
└─────────────────┘

[后续请求]
     │
     ▼
请求头: Authorization: Bearer <access_token>
     │
     ▼
┌─────────────────┐
│  后端验证 Token  │
│  - 解码 JWT     │
│  - 检查有效期    │
│  - 提取 user_id  │
└────────┬────────┘
         │
         ▼
    允许访问 / 401 Unauthorized

[Token 过期时]
     │
     ▼
401 Unauthorized
     │
     ▼
┌─────────────────┐
│  前端自动刷新    │
│  POST /refresh   │
│  (refresh_token) │
└────────┬────────┘
         │
         ▼
    新的 Access Token
```

#### 3.2.2 认证 API 接口

| 方法 | 路径 | 描述 | 请求体 | 响应 |
|------|------|------|--------|------|
| POST | `/api/auth/register` | 用户注册 | `{username, email, password}` | `{user, access_token, refresh_token}` |
| POST | `/api/auth/login` | 用户登录 | `{email, password}` | `{access_token, refresh_token}` |
| POST | `/api/auth/refresh` | 刷新 Token | `{refresh_token}` | `{access_token, refresh_token}` |
| POST | `/api/auth/logout` | 用户登出 | - | `{message: "success"}` |
| GET | `/api/auth/me` | 获取当前用户 | - | `{user}` |
| PUT | `/api/auth/password` | 修改密码 | `{old_password, new_password}` | `{message: "success"}` |

#### 3.2.3 前端认证状态管理

**authStore.ts** (Zustand):

```typescript
interface AuthState {
  // 状态
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  isInitialized: boolean;

  // 操作
  login: (email: string, password: string) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  refreshAccessToken: () => Promise<void>;
  initialize: () => Promise<void>;
}

// 持久化中间件 - 自动保存 Token 到 localStorage
const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      isInitialized: false,

      login: async (email, password) => {
        set({ isLoading: true });
        try {
          const response = await authApiClient.login({ email, password });
          set({
            user: response.user,
            accessToken: response.access_token,
            refreshToken: response.refresh_token,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      // ... 其他方法
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
      }),
    }
  )
);
```

### 3.3 多模态交互

#### 3.3.1 图片理解

**功能**:
- 支持上传图片 (JPG/PNG/GIF/WebP)
- 支持粘贴剪贴板图片
- 支持拖拽上传
- AI 分析图片内容并回答问题

**技术实现**:

1. **前端图片处理** (`InputArea.tsx`):

```typescript
const handleImageUpload = async (files: File[]) => {
  const processedImages = await Promise.all(
    files.map(async (file) => {
      // 压缩图片 (最大 2MB)
      const compressed = await compressImage(file, { maxWidth: 1920, quality: 0.8 });
      // 转换为 Base64
      return {
        data: await fileToBase64(compressed),
        name: file.name,
        type: file.type,
      };
    })
  );
  setImages((prev) => [...prev, ...processedImages]);
};
```

2. **后端多模态消息构建** (`agent_service.py`):

```python
def build_multimodal_content(content: str, images: List[str]) -> dict:
    """构建多模态消息"""
    parts = []

    # 添加图片
    for img_base64 in images:
        parts.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{img_base64}"
            }
        })

    # 添加文本
    parts.append({
        "type": "text",
        "text": content
    })

    return {"role": "user", "content": parts}
```

#### 3.3.2 语音交互

**语音输入 (STT)**:

1. **前端录音** (`VoiceRecorder.tsx`):

```typescript
const startRecording = async () => {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder.current = new MediaRecorder(stream);

  mediaRecorder.current.ondataavailable = (event) => {
    audioChunks.current.push(event.data);
  };

  mediaRecorder.current.start();
  setIsRecording(true);
};
```

2. **后端识别** (`whisper_service.py`):

```python
from faster_whisper import WhisperModel

model = WhisperModel("base", device="cpu", compute_type="int8")

def transcribe_audio(audio_bytes: bytes, language: str = "zh") -> str:
    """语音转文字"""
    segments, info = model.transcribe(
        audio_bytes,
        language=language,
        beam_size=5
    )
    return "".join([segment.text for segment in segments])
```

**语音输出 (TTS)**:

```python
import edge_tts

async def synthesize_speech(text: str, voice: str = "zh-CN-XiaoxiaoNeural") -> bytes:
    """文字转语音"""
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate="+0%"
    )

    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]

    return audio_data
```

### 3.4 RAG 知识库

#### 3.4.1 混合检索架构

```
用户查询
     │
     ▼
┌─────────────────────────────────┐
│     SearchService              │
│  - 接收查询                      │
│  - 并行检索                      │
└────────┬────────────────────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌─────────┐ ┌─────────┐
│ Vector  │ │  BM25   │
│ Search  │ │  Search │
│ (Pgvector)│ (jieba分词)│
└────┬────┘ └────┬────┘
     │           │
     └─────┬─────┘
           │ RRF Fusion
           │ score = α/(k+rank_vec) + (1-α)/(k+rank_bm25)
           ▼
     ┌──────────┐
     │ Reranker │
     │ (bge-reranker)│
     └─────┬────┘
           │
           ▼
     ┌──────────┐
     │ Top-K    │
     │ Results  │
     └──────────┘
```

**参数配置**:
- `chunk_size`: 1500 字符
- `overlap`: 200 字符
- `top_k`: 10 个结果
- `alpha`: 0.5 (向量/BM25 权重)

#### 3.4.2 引用追溯

**Citation 数据结构**:

```python
class Citation(BaseModel):
    source_id: str              # 文档 ID
    source_name: str            # 文档名称
    chunk_id: str               # 分块 ID
    page_number: Optional[int] # 页码
    content: str                # 引用内容
    similarity: float           # 相似度分数
```

**前端展示** (`CitationPanel.tsx`):

```typescript
interface CitationPanelProps {
  citations: Citation[];
  onExpand: (citation: Citation) => void;
}

// 显示引用列表
<div className="citations-list">
  {citations.map((citation) => (
    <div key={citation.chunk_id} className="citation-item">
      <div className="citation-source">
        📄 {citation.source_name}
        {citation.page_number && ` (P.${citation.page_number})`}
      </div>
      <div className="citation-content">
        {citation.content.slice(0, 100)}...
      </div>
      <Button onClick={() => onExpand(citation)}>
        查看完整内容
      </Button>
    </div>
  ))}
</div>
```

### 3.5 演示文稿生成

#### 3.5.1 AI 生成流程

```
用户输入 "生成关于人工智能的 PPT"
     │
     ▼
┌─────────────────────────────────┐
│  PresentationService            │
│  - 解析用户需求                  │
│  - 确定主题、受众、类型          │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  LLM 大纲生成                    │
│  - 生成幻灯片结构                │
│  - 每张标题和要点                │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  LayoutEngine                    │
│  - 根据内容类型选择布局          │
│  - 19 种布局类型                │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  ThemeService                    │
│  - 应用主题样式                  │
│  - 17 种精品主题                │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  ImageService                    │
│  - 根据内容推荐图片               │
│  - Unsplash API                  │
└────────┬────────────────────────┘
         │
         ▼
    完整的演示文稿数据
```

#### 3.5.2 布局类型 (19 种)

| 布局 ID | 名称 | 适用场景 |
|---------|------|----------|
| `title_cover` | 封面页 | 演讲文稿首页 |
| `title_section` | 章节页 | 新章节开始 |
| `bullet_points` | 列表页 | 要点列表 |
| `two_column` | 双栏布局 | 对比/并列 |
| `three_column` | 三栏布局 | 三个维度 |
| `comparison` | 对比布局 | 优劣势对比 |
| `image_left` | 左图右文 | 图文混排 |
| `image_right` | 右图左文 | 图文混排 |
| `image_full` | 全屏图片 | 大图展示 |
| `quote_center` | 引用页 | 名言引用 |
| `metric_card` | 指标卡片 | 数据指标 |
| `timeline` | 时间线 | 发展历程 |
| `process_flow` | 流程图 | 步骤流程 |
| `data_table` | 数据表格 | 结构化数据 |
| `chart_single` | 单图表 | 数据可视化 |
| `chart_dual` | 双图表 | 数据对比 |
| `gallery` | 图片画廊 | 多图展示 |
| `thank_you` | 结尾页 | 感谢页面 |

#### 3.5.3 主题系统 (17 种)

| 主题 ID | 名称 | 适用场景 |
|---------|------|----------|
| `modern_business` | 现代商务 | 商业汇报 |
| `corporate_blue` | 企业蓝 | 公司介绍 |
| `classic_blue` | 经典蓝 | 学术演讲 |
| `teal_coral` | 青色珊瑚 | 创意展示 |
| `elegant_dark` | 优雅暗色 | 奢华产品 |
| `dark_tech` | 暗黑科技 | 技术分享 |
| `gradient_purple` | 紫色渐变 | 艺术展示 |
| `neon_future` | 霓虹未来 | 科幻主题 |
| `minimal_white` | 极简白 | 简约风格 |
| `nature_green` | 自然绿 | 环保主题 |
| `soft_pastel` | 柔和粉 | 女性主题 |
| `creative_colorful` | 创意彩色 | 设计展示 |
| `warm_sunset` | 温暖日落 | 情感主题 |
| `academic_classic` | 学术经典 | 学术报告 |
| `anime_dark` | 二次元暗黑 | 动漫游戏 |
| `anime_cute` | 二次元可爱 | 萌系主题 |
| `cyberpunk` | 赛博朋克 | 科幻主题 |

#### 3.5.4 在线编辑器功能

**实时编辑**:
- 标题/内容/备注实时修改
- 1 秒防抖自动保存
- 布局类型动态切换
- 主题即时预览

**幻灯片操作**:
- 插入新幻灯片 (任意位置)
- 删除幻灯片
- 复制幻灯片
- 拖拽排序 (规划中)

**AI 对话式修改**:
- 自然语言指令解析
- "把第3页标题改为xxx"
- "在当前页后插入新幻灯片"
- "把主题换成暗色科技"

---

## 四、后端服务详解

### 4.1 服务架构总览

My-Chat-LangChain V9.0 采用微服务架构，将后端拆分为 5 个独立的服务：

```
backend/
├── auth-service/         # 认证服务 (端口 8001)
├── chat-service/         # 聊天服务 (端口 8002)
├── whisper-service/      # 语音服务 (端口 8003)
├── rag-service/          # RAG 检索服务 (端口 8004)
└── presentation-service/ # 演示文稿服务 (端口 8005)
```

| 服务 | 端口 | 职责 | 技术栈 |
|------|------|------|--------|
| **auth-service** | 8001 | 用户认证、JWT Token 管理 | FastAPI + SQLAlchemy + JWT |
| **chat-service** | 8002 | LangGraph Agent、会话管理 | FastAPI + LangGraph + LangChain |
| **whisper-service** | 8003 | 语音识别/合成 | FastAPI + faster-whisper + edge-tts |
| **rag-service** | 8004 | 向量检索、BM25、文档解析 | FastAPI + pgvector/Milvus + jieba |
| **presentation-service** | 8005 | AI 生成 PPT、主题、导出 | FastAPI + python-pptx |

---

### 4.2 Auth Service (认证服务)

#### 4.2.1 服务概述

`auth-service` 负责用户认证和授权，是整个系统的安全基石。

**核心功能**：
- 用户注册/登录
- JWT Token 生成与验证
- Token 自动刷新机制
- 用户信息管理
- 密码加密存储 (bcrypt)

#### 4.2.2 项目结构

```
backend/auth-service/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 应用入口
│   ├── config.py               # 配置管理
│   ├── database.py             # 数据库连接
│   ├── core/                   # 核心模块
│   │   ├── __init__.py
│   │   ├── config.py           # 配置类
│   │   ├── security.py         # 密码加密、Token 生成
│   │   └── deps.py             # 依赖注入
│   ├── models/                 # SQLAlchemy 模型
│   │   ├── __init__.py
│   │   └── user.py             # 用户数据模型
│   ├── schemas/                # Pydantic Schema
│   │   ├── __init__.py
│   │   ├── user.py             # 用户 Schema
│   │   └── token.py            # Token Schema
│   ├── services/               # 业务逻辑
│   │   ├── __init__.py
│   │   └── user_service.py     # 用户服务
│   └── api/v1/                 # API 路由
│       ├── __init__.py
│       ├── auth.py             # 认证路由
│       └── users.py            # 用户路由
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # pytest 配置
│   └── test_auth.py            # 认证测试
├── requirements.txt
└── .env                        # 环境变量
```

#### 4.2.3 核心实现

**1. 应用入口 (main.py)**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.database import init_db
from app.api.v1 import auth, users

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    print("Initializing database...")
    await init_db()
    print("Database initialized successfully.")
    yield
    print("Shutting down...")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Authentication service for Stream-Agent V9",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由注册
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "service": "auth-service"}
```

**2. 安全模块 (security.py)**

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建 Access Token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """创建 Refresh Token (7天有效期)"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Optional[dict]:
    """解码 Token"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None
```

**3. 认证 API (api/v1/auth.py)**

```python
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.schemas.token import TokenResponse
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.core.deps import get_current_user

router = APIRouter(prefix="/v1/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    用户注册

    - 验证用户名/邮箱唯一性
    - 密码加密存储
    - 注册成功自动登录
    """
    # 检查用户名是否存在
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already registered")

    # 检查邮箱是否存在
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # 创建新用户
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # 生成 Token
    access_token = create_access_token({"sub": str(new_user.id)})
    refresh_token = create_refresh_token({"sub": str(new_user.id)})

    return {
        "user": new_user,
        "access_token": access_token,
        "refresh_token": refresh_token
    }

@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    用户登录

    - 支持用户名或邮箱登录
    - 返回 Access Token (15分钟) 和 Refresh Token (7天)
    """
    # 查找用户
    result = await db.execute(
        select(User).where(
            (User.username == form_data.username) | (User.email == form_data.username)
        )
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    # 生成 Token
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    """刷新 Access Token"""
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # 生成新的 Access Token
    new_access_token = create_access_token({"sub": str(user.id)})

    return {
        "access_token": new_access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """用户登出 (前端删除 Token 即可)"""
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user
```

**4. 用户模型 (models/user.py)**

```python
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.database import Base

class User(Base):
    """用户表模型"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"
```

#### 4.2.4 API 端点清单

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| POST | `/api/v1/auth/register` | 用户注册 | 否 |
| POST | `/api/v1/auth/login` | 用户登录 | 否 |
| POST | `/api/v1/auth/refresh` | 刷新 Token | 否 |
| POST | `/api/v1/auth/logout` | 用户登出 | 是 |
| GET | `/api/v1/auth/me` | 获取当前用户 | 是 |
| PUT | `/api/v1/users/{id}` | 更新用户信息 | 是 |
| DELETE | `/api/v1/users/{id}` | 删除用户 | 是 |

---

### 4.3 Chat Service (聊天服务)

#### 4.3.1 服务概述

`chat-service` 是系统的核心，负责处理用户聊天请求、管理会话、调用 LangGraph Agent。

**核心功能**：
- LangGraph ReAct Agent 调用
- 会话 (Conversation) 管理
- 消息 (Message) 持久化
- SSE 流式响应
- 96+ 工具调用管理

#### 4.3.2 项目结构

```
backend/chat-service/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 应用入口
│   ├── config.py               # 配置管理
│   ├── database.py             # 数据库连接
│   ├── models/                 # SQLAlchemy 模型
│   │   ├── __init__.py
│   │   ├── conversation.py     # 会话模型
│   │   └── message.py          # 消息模型
│   ├── schemas/                # Pydantic Schema
│   │   ├── __init__.py
│   │   ├── chat.py             # 聊天 Schema
│   │   ├── conversation.py     # 会话 Schema
│   │   └── message.py          # 消息 Schema
│   ├── services/               # 业务逻辑
│   │   ├── __init__.py
│   │   ├── agent_service.py    # LangGraph Agent 核心
│   │   ├── llm_service.py      # LLM 调用封装
│   │   └── conversation_service.py  # 会话服务
│   ├── tools/                  # LangChain 工具集
│   │   ├── __init__.py
│   │   ├── rag_tools.py        # RAG 检索工具
│   │   ├── e2b_tools.py        # E2B 代码执行工具
│   │   ├── search_tools.py     # 搜索工具
│   │   ├── mcp_tools.py        # MCP 工具适配器
│   │   └── presentation_tools.py  # PPT 生成工具
│   └── api/v1/                 # API 路由
│       ├── __init__.py
│       ├── chat.py             # 聊天路由
│       ├── conversation.py     # 会话管理路由
│       └── upload.py           # 文件上传路由
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_agent.py          # Agent 测试
└── requirements.txt
```

#### 4.3.3 LangGraph Agent 实现

**1. Agent Service (services/agent_service.py)**

```python
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from app.tools.rag_tools import rag_search, list_knowledge_documents
from app.tools.e2b_tools import execute_python_code, analyze_csv_data, generate_chart
from app.tools.search_tools import search_engine, scrape_as_markdown
from app.tools.presentation_tools import generate_presentation
from app.core.config import settings

# Agent System Prompt
SYSTEM_PROMPT = """
# Stream-Agent v9.0 - AI Research Assistant

You are an AI research assistant equipped with powerful tools for:
- Web Search & Scraping
- E-commerce Data (Amazon, Walmart, eBay, Etsy)
- Social Media (LinkedIn, Instagram, Facebook, TikTok, X/Twitter, YouTube, Reddit)
- Academic Research (arXiv, PubMed, Google Scholar)
- Knowledge Base (RAG)
- Code Execution (E2B Sandbox)

## RAG Knowledge Base Usage (重要)
当使用 rag_search 工具时:
1. **必须使用检索结果**: 当 rag_search 返回相关内容时，你必须基于这些内容来回答问题
2. **综合多条结果**: 检索会返回多条相关片段，请综合这些内容给出完整答案
3. **引用来源**: 在回答中提及内容来自哪个文档或页码

## Response Format
- 基于工具结果给出详细、准确的回答
- 引用数据来源时注明出处
- 代码执行结果要清晰展示
- 对不确定的信息诚实说明
"""

async def get_tools(api_keys: dict = None) -> list:
    """加载可用工具"""
    custom_tools = [
        rag_search,
        list_knowledge_documents,
        search_engine,
        scrape_as_markdown,
        execute_python_code,
        analyze_csv_data,
        generate_chart,
        generate_presentation,
    ]
    return custom_tools

class AgentState(TypedDict):
    """Agent 状态定义"""
    messages: List[BaseMessage]
    user_id: str
    conversation_id: str
    tool_calls: List[dict]
    next_action: str

async def create_graph():
    """创建 LangGraph Agent"""
    # 定义节点
    async def call_model(state: AgentState, config: dict):
        """调用 LLM"""
        messages = state["messages"]
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            api_key=settings.GOOGLE_API_KEY,
            temperature=0.7,
        )
        response = await llm.ainvoke(messages)
        return {"messages": [response]}

    async def call_tools(state: AgentState, config: dict):
        """执行工具"""
        messages = state["messages"]
        last_message = messages[-1]

        tool_calls = []
        tool_outputs = []

        if hasattr(last_message, "tool_calls"):
            for tool_call in last_message.tool_calls:
                tool_calls.append({
                    "name": tool_call.name,
                    "args": tool_call.args,
                    "id": tool_call.id
                })

                # 执行工具
                tools = await get_tools()
                tool_map = {tool.name: tool for tool in tools}

                if tool_call.name in tool_map:
                    try:
                        result = await tool_map[tool_call.name].ainvoke(tool_call.args)
                        tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "output": result
                        })
                    except Exception as e:
                        tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "output": f"Error: {str(e)}"
                        })

        return {
            "tool_calls": tool_calls,
            "tool_outputs": tool_outputs
        }

    def should_continue(state: AgentState) -> str:
        """决定下一步动作"""
        messages = state["messages"]
        last_message = messages[-1]

        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return END

    # 构建图
    workflow = StateGraph(AgentState)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", call_tools)
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges("agent", should_continue)
    workflow.add_edge("tools", "agent")

    return workflow.compile()

async def stream_chat_response(user_message: str, conversation_id: str, user_id: str):
    """流式聊天响应"""
    graph = await create_graph()

    inputs = {
        "messages": [HumanMessage(content=user_message)],
        "user_id": user_id,
        "conversation_id": conversation_id,
        "tool_calls": [],
        "next_action": ""
    }

    async for event in graph.astream(inputs, stream_mode="values"):
        # 生成 SSE 事件
        if "messages" in event:
            last_message = event["messages"][-1]
            if isinstance(last_message, AIMessage):
                yield {
                    "event": "text",
                    "data": {"content": last_message.content, "delta": True}
                }

        if "tool_calls" in event and event["tool_calls"]:
            for tool_call in event["tool_calls"]:
                yield {
                    "event": "tool_start",
                    "data": {"tool_name": tool_call["name"], "tool_id": tool_call["id"]}
                }

        if "tool_outputs" in event and event["tool_outputs"]:
            for output in event["tool_outputs"]:
                yield {
                    "event": "tool_end",
                    "data": {"tool_id": output["tool_call_id"], "output": output["output"]}
                }

    yield {"event": "done", "data": {"message_id": "xxx"}}
```

**2. 聊天 API (api/v1/chat.py)**

```python
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.chat import ChatRequest
from app.services.agent_service import stream_chat_response
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/v1/chat", tags=["Chat"])

@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    流式聊天接口 (SSE)

    - 支持 SSE 实时流式响应
    - 工具调用可视化
    - 会话上下文管理
    """
    async def event_generator():
        try:
            async for event in stream_chat_response(
                user_message=request.content,
                conversation_id=request.conversation_id,
                user_id=str(current_user.id)
            ):
                yield f"event: {event['event']}\n"
                yield f"data: {json.dumps(event['data'])}\n\n"
        except Exception as e:
            yield f"event: error\n"
            yield f"data: {json.dumps({'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@router.post("/stop")
async def stop_stream(
    request: StopRequest,
    current_user: User = Depends(get_current_user)
):
    """停止当前生成"""
    # 实现停止逻辑
    return {"message": "Generation stopped"}

@router.post("/regenerate")
async def regenerate_message(
    request: RegenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """重新生成上一条回复"""
    # 获取最后一条消息并重新生成
    pass
```

#### 4.3.4 数据模型

**会话模型 (models/conversation.py)**

```python
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
import uuid

class Conversation(Base):
    """会话表"""
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), default="New Chat")
    model = Column(String(50), default="gemini-2.0-flash-exp")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
```

**消息模型 (models/message.py)**

```python
from sqlalchemy import Column, Text, JSON, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
import enum

class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class Message(Base):
    """消息表"""
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    images = Column(JSONB, default=list)  # Base64 图片数组
    tool_calls = Column(JSONB, default=list)  # 工具调用记录
    citations = Column(JSONB, default=list)  # RAG 引用
    created_at = Column(DateTime, server_default=func.now())

    conversation = relationship("Conversation", back_populates="messages")
```

---

### 4.4 RAG Service (检索增强服务)

#### 4.4.1 服务概述

`rag-service` 负责文档解析、向量存储、混合检索、引用追溯。

**核心功能**：
- 混合检索 (向量相似度 + BM25 关键词)
- RRF (Reciprocal Rank Fusion) 融合算法
- Reranker 重排序
- 智能分块 (语义/页面感知/递归)
- 引用追溯
- 双后端支持 (pgvector / Milvus)

#### 4.4.2 项目结构

```
backend/rag-service/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 应用入口
│   ├── config.py               # 配置管理
│   ├── database.py             # 数据库连接
│   ├── models/                 # SQLAlchemy 模型
│   │   ├── __init__.py
│   │   ├── document.py         # 文档模型
│   │   └── chunk.py            # 分块模型
│   ├── schemas/                # Pydantic Schema
│   │   ├── __init__.py
│   │   ├── document.py         # 文档 Schema
│   │   └── search.py           # 检索 Schema
│   ├── services/               # 核心服务
│   │   ├── __init__.py
│   │   ├── pgvector_service.py # pgvector 向量存储
│   │   ├── milvus_service.py   # Milvus 向量存储
│   │   ├── bm25_service.py     # BM25 关键词检索
│   │   ├── search_service.py   # 混合检索服务
│   │   ├── rerank_service.py   # 重排序服务
│   │   ├── chunking_service.py # 智能分块服务
│   │   ├── citation_service.py # 引用追溯服务
│   │   └── embedding_service.py # Embedding 服务
│   └── api/v1/                 # API 路由
│       ├── __init__.py
│       ├── documents.py        # 文档管理
│       ├── search.py           # 检索接口
│       └── ingest.py           # 文档摄取
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_search_service.py # 混合检索测试
│   └── test_chunking.py       # 分块测试
└── requirements.txt
```

#### 4.4.3 混合检索实现

**Search Service (services/search_service.py)**

```python
from typing import List, Tuple, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.pgvector_service import PgvectorService
from app.services.milvus_service import MilvusService
from app.services.bm25_service import BM25Service
from app.services.rerank_service import RerankerService
from app.services.embedding_service import EmbeddingService
from app.schemas.search import SearchResult, VectorSearchResult, BM25Result

class HybridSearchService:
    """
    混合检索服务 - 向量相似度 + BM25 关键词 + RRF 融合 + Reranker
    """

    def __init__(self, vector_service, bm25_service: BM25Service,
                 reranker: Optional[RerankerService] = None):
        """
        初始化混合检索服务

        Args:
            vector_service: 向量检索服务 (pgvector 或 milvus)
            bm25_service: BM25 关键词检索服务
            reranker: 重排序服务 (可选)
        """
        self.milvus = vector_service
        self.bm25 = bm25_service
        self.reranker = reranker

    def rrf_fusion(
        self,
        vector_results: List[VectorSearchResult],
        bm25_results: List[BM25Result],
        alpha: float = 0.5,
        k: int = 60
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Reciprocal Rank Fusion (RRF) 融合算法

        公式: RRF(d) = Σ (1 / (k + r_i)) for each ranking r_i

        Args:
            vector_results: 向量检索结果
            bm25_results: BM25 检索结果
            alpha: 向量检索权重 (0-1)，bm25 权重为 (1-alpha)
            k: RRF 常数，用于平滑排名影响

        Returns:
            融合后的结果列表 [(chunk_id, {score, vector_rank, bm25_rank, ...})]
        """
        scores: Dict[str, Dict[str, Any]] = {}

        # 处理向量检索结果
        for rank, result in enumerate(vector_results):
            chunk_id = result.id
            rrf_score = alpha / (k + rank + 1)  # rank 从 0 开始

            if chunk_id not in scores:
                scores[chunk_id] = {
                    "chunk_id": chunk_id,
                    "fused_score": 0,
                    "vector_rank": rank + 1,
                    "bm25_rank": None,
                    "vector_score": result.score,
                    "bm25_score": None
                }
            scores[chunk_id]["fused_score"] += rrf_score

        # 处理 BM25 检索结果
        for rank, result in enumerate(bm25_results):
            chunk_id = result.id
            rrf_score = (1 - alpha) / (k + rank + 1)

            if chunk_id not in scores:
                scores[chunk_id] = {
                    "chunk_id": chunk_id,
                    "fused_score": 0,
                    "vector_rank": None,
                    "bm25_rank": rank + 1,
                    "vector_score": None,
                    "bm25_score": result.score
                }
            scores[chunk_id]["fused_score"] += rrf_score
            if "bm25_rank" not in scores[chunk_id]:
                scores[chunk_id]["bm25_rank"] = rank + 1

        # 按融合分数排序
        sorted_results = sorted(scores.items(), key=lambda x: x[1]["fused_score"], reverse=True)
        return sorted_results

    async def _rerank(
        self,
        query: str,
        candidates: List[Tuple[str, Dict[str, Any]]],
        top_k: int
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """
        使用 Reranker 重新排序

        Args:
            query: 查询文本
            candidates: 候选结果
            top_k: 返回 top-k 结果

        Returns:
            重排序后的结果
        """
        if not self.reranker:
            return candidates[:top_k]

        # 提取候选文档内容
        documents = [result[1].get("content", "") for result in candidates]

        # 调用 Reranker
        rerank_scores = await self.reranker.rerank(query, documents)

        # 更新分数并重新排序
        for i, (chunk_id, data) in enumerate(candidates):
            if i < len(rerank_scores):
                data["rerank_score"] = rerank_scores[i]
                data["fused_score"] = rerank_scores[i]  # 使用 rerank 分数作为新分数

        return sorted(candidates, key=lambda x: x[1]["fused_score"], reverse=True)[:top_k]

    async def search(
        self,
        query: str,
        top_k: int = 10,
        alpha: float = 0.5,
        user_id: Optional[str] = None,
        use_rerank: bool = True,
        filters: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[SearchResult], float]:
        """
        执行混合检索

        Args:
            query: 查询文本
            top_k: 返回结果数量
            alpha: 向量检索权重 (0-1)
            user_id: 用户 ID (用于权限过滤)
            use_rerank: 是否使用 Reranker
            filters: 额外过滤条件

        Returns:
            (搜索结果列表, 检索耗时秒)
        """
        import time
        start_time = time.time()

        # 1. 生成查询向量
        embedding_service = EmbeddingService()
        query_embedding = await embedding_service.embed_query(query)

        # 2. 并行执行向量检索和 BM25 检索
        vector_results = await self.milvus.search(
            query_embedding=query_embedding,
            top_k=top_k * 2,  # 获取更多候选用于融合
            user_id=user_id,
            filters=filters
        )

        bm25_results = await self.bm25.search(
            query=query,
            top_k=top_k * 2,
            user_id=user_id,
            filters=filters
        )

        # 3. RRF 融合
        fused_results = self.rrf_fusion(vector_results, bm25_results, alpha=alpha)

        # 4. Reranker 重排序 (可选)
        if use_rerank and self.reranker:
            fused_results = await self._rerank(query, fused_results, top_k)
        else:
            fused_results = fused_results[:top_k]

        # 5. 构建最终结果
        search_results = []
        for chunk_id, data in fused_results:
            # 从原始结果中获取详细信息
            chunk_data = self._get_chunk_details(chunk_id)
            if chunk_data:
                search_results.append(SearchResult(
                    id=chunk_id,
                    document_id=chunk_data["document_id"],
                    document_name=chunk_data["document_name"],
                    content=chunk_data["content"],
                    page_number=chunk_data.get("page_number"),
                    similarity=data.get("vector_score", 0),
                    score=data["fused_score"],
                    metadata=chunk_data.get("metadata", {})
                ))

        elapsed_time = time.time() - start_time
        return search_results, elapsed_time
```

#### 4.4.4 应用入口 (main.py)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.database import init_db
from app.services.embedding_service import EmbeddingService
from app.services.pgvector_service import PgvectorService
from app.services.milvus_service import MilvusService
from app.services.bm25_service import BM25Service
from app.services.search_service import HybridSearchService
from app.services.rerank_service import RerankerService
from app.api.v1 import documents, search, ingest

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}...")

    # 初始化数据库
    init_db()

    # 初始化 Embedding 服务
    app.state.embedding_service = EmbeddingService()
    print("Embedding service initialized.")

    # 初始化向量存储 (双后端支持)
    if settings.VECTOR_STORE_BACKEND == "milvus" and settings.MILVUS_ENABLED:
        from app.services.milvus_service import MilvusService
        app.state.milvus_service = MilvusService()
        app.state.vector_service = app.state.milvus_service
        print("Using Milvus as vector backend.")
    else:
        from app.services.pgvector_service import PgvectorService
        app.state.vector_service = PgvectorService()
        app.state.vector_service.connect()
        print("Using pgvector as vector backend.")

    # 初始化 BM25 服务
    app.state.bm25_service = BM25Service()
    print("BM25 service initialized.")

    # 初始化 Reranker (可选)
    if settings.RERANKER_ENABLED:
        app.state.reranker_service = RerankerService()
        print("Reranker service initialized.")

    # 初始化混合检索服务
    app.state.search_service = HybridSearchService(
        vector_service=app.state.vector_service,
        bm25_service=app.state.bm25_service,
        reranker=getattr(app.state, "reranker_service", None)
    )
    print("Hybrid search service initialized.")

    yield

    print("Shutting down...")
    if hasattr(app.state, "vector_service"):
        app.state.vector_service.close()
    print("Shutdown complete.")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="RAG Service for Stream-Agent V9 - Hybrid search with vector + BM25",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router, prefix="/api")
app.include_router(search.router, prefix="/api")
app.include_router(ingest.router, prefix="/api")

@app.get("/health")
async def health_check():
    """健康检查"""
    health = {
        "status": "healthy",
        "service": settings.APP_NAME,
        "vector_backend": settings.VECTOR_STORE_BACKEND,
        "vector_connected": False,
    }
    if app.state.vector_service.is_connected():
        health["vector_connected"] = True
        stats = app.state.vector_service.get_collection_stats()
        health["collection_stats"] = stats
    return health
```

#### 4.4.5 API 端点清单

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| **文档管理** |
| GET | `/api/v1/documents` | 获取文档列表 | 是 |
| POST | `/api/v1/documents/upload` | 上传文档 | 是 |
| DELETE | `/api/v1/documents/{id}` | 删除文档 | 是 |
| GET | `/api/v1/documents/{id}/status` | 获取处理状态 | 是 |
| **检索** |
| POST | `/api/v1/search` | 混合检索 | 是 |
| POST | `/api/v1/search/vector` | 纯向量检索 | 是 |
| POST | `/api/v1/search/bm25` | 纯 BM25 检索 | 是 |
| **文档摄取** |
| POST | `/api/v1/ingest/url` | 从 URL 摄取 | 是 |
| POST | `/api/v1/ingest/text` | 摄取文本 | 是 |

---

### 4.5 Presentation Service (演示文稿服务)

#### 4.5.1 服务概述

`presentation-service` 负责生成、编辑、导出演示文稿。

**核心功能**：
- AI 生成 PPT 大纲
- 19 种专业布局类型
- 17 种精品主题
- 在线编辑器
- 导出 HTML / PPTX
- AI 对话式修改

#### 4.5.2 项目结构

```
backend/presentation-service/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 应用入口
│   ├── config.py               # 配置管理
│   ├── database.py             # 数据库连接
│   ├── models/                 # SQLAlchemy 模型
│   │   ├── __init__.py
│   │   ├── presentation.py     # 演示文稿模型
│   │   └── slide_version.py    # 幻灯片版本模型
│   ├── schemas/                # Pydantic Schema
│   │   ├── __init__.py
│   │   ├── presentation.py     # 演示文稿 Schema
│   │   └── slide.py            # 幻灯片 Schema
│   ├── services/               # 核心服务
│   │   ├── __init__.py
│   │   ├── presentation_service.py  # AI 生成 PPT
│   │   ├── layout_engine.py         # 19 种布局引擎
│   │   ├── theme_service.py          # 17 种主题系统
│   │   ├── image_service.py          # 图片服务
│   │   ├── export_service.py         # HTML 导出
│   │   ├── pptx_export_service.py    # PPTX 导出
│   │   └── intent_parser.py          # AI 对话式修改
│   └── api/v1/                 # API 路由
│       ├── __init__.py
│       ├── presentations.py    # CRUD API
│       ├── editor.py           # 编辑器 API
│       └── export.py           # 导出 API
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_presentation_service.py
│   ├── test_layout_engine.py
│   ├── test_theme_service.py
│   ├── test_export_service.py
│   └── test_pptx_export_service.py
└── requirements.txt
```

#### 4.5.3 布局引擎

**19 种布局类型 (layout_engine.py)**

```python
from enum import Enum
from typing import List, Dict, Any

class LayoutType(str, Enum):
    """布局类型枚举"""
    # === 基础布局 ===
    TITLE_COVER = "title_cover"           # 封面页
    TITLE_SECTION = "title_section"       # 章节页
    BULLET_POINTS = "bullet_points"       # 列表页
    TWO_COLUMN = "two_column"             # 双栏布局
    THREE_COLUMN = "three_column"         # 三栏布局
    IMAGE_TEXT = "image_text"             # 图文混排

    # === 数据展示 ===
    CHART_SINGLE = "chart_single"         # 单图表
    CHART_DUAL = "chart_dual"             # 双图表
    DATA_TABLE = "data_table"             # 数据表格
    METRIC_CARD = "metric_card"           # 指标卡片

    # === 特殊效果 ===
    QUOTE_CENTER = "quote_center"         # 引用页
    TIMELINE = "timeline"                 # 时间线
    PROCESS_FLOW = "process_flow"         # 流程图
    COMPARISON = "comparison"             # 对比布局
    GALLERY = "gallery"                   # 图片画廊

    # === 变体 ===
    IMAGE_LEFT = "image_left"             # 左图右文
    IMAGE_RIGHT = "image_right"           # 右图左文
    IMAGE_FULL = "image_full"             # 全屏图片
    THANK_YOU = "thank_you"               # 感谢页
    CONTACT = "contact"                   # 联系方式

class LayoutEngine:
    """布局引擎 - 根据内容类型智能推荐布局"""

    CONTENT_LAYOUT_MAPPING = {
        "cover": LayoutType.TITLE_COVER,
        "section": LayoutType.TITLE_SECTION,
        "list": LayoutType.BULLET_POINTS,
        "comparison": LayoutType.COMPARISON,
        "quote": LayoutType.QUOTE_CENTER,
        "data": LayoutType.DATA_TABLE,
        "chart": LayoutType.CHART_SINGLE,
        "image": LayoutType.IMAGE_TEXT,
        "timeline": LayoutType.TIMELINE,
        "process": LayoutType.PROCESS_FLOW,
    }

    def recommend_layout(self, content_type: str, content_length: int = 0) -> LayoutType:
        """根据内容类型推荐布局"""
        if content_type in self.CONTENT_LAYOUT_MAPPING:
            return self.CONTENT_LAYOUT_MAPPING[content_type]

        # 基于内容长度推荐
        if content_length < 100:
            return LayoutType.QUOTE_CENTER
        elif content_length < 300:
            return LayoutType.BULLET_POINTS
        else:
            return LayoutType.TWO_COLUMN

    def get_layout_template(self, layout: LayoutType) -> Dict[str, Any]:
        """获取布局模板配置"""
        templates = {
            LayoutType.TITLE_COVER: {
                "has_title": True,
                "has_content": True,
                "has_images": False,
                "content_position": "center",
                "max_content_length": 200
            },
            LayoutType.BULLET_POINTS: {
                "has_title": True,
                "has_content": True,
                "has_images": False,
                "content_position": "left",
                "max_content_length": 800,
                "max_bullets": 8
            },
            # ... 更多布局模板
        }
        return templates.get(layout, {})
```

#### 4.5.4 主题系统

**17 种主题 (theme_service.py)**

```python
from typing import Dict, Any

class ThemeService:
    """主题系统 - 17 种精品主题"""

    THEMES = {
        "modern_business": {
            "name": "现代商务",
            "colors": {
                "primary": "#1E3A8A",
                "secondary": "#3B82F6",
                "background": "#FFFFFF",
                "text": "#1E293B",
                "accent": "#60A5FA"
            },
            "fonts": {"title": "Arial", "body": "Arial"},
            "style": "clean, professional"
        },
        "corporate_blue": {
            "name": "企业蓝",
            "colors": {
                "primary": "#1E40AF",
                "secondary": "#2563EB",
                "background": "#FFFFFF",
                "text": "#1F2937",
                "accent": "#3B82F6"
            },
            "fonts": {"title": "Arial", "body": "Arial"},
            "style": "corporate, trustworthy"
        },
        "classic_blue": {
            "name": "经典蓝",
            "colors": {
                "primary": "#1C2833",
                "secondary": "#AAB7B8",
                "background": "#F4F6F6",
                "text": "#2E4053",
                "accent": "#1C2833"
            },
            "fonts": {"title": "Georgia", "body": "Arial"},
            "style": "academic, formal"
        },
        "teal_coral": {
            "name": "青色珊瑚",
            "colors": {
                "primary": "#277884",
                "secondary": "#5EA8A7",
                "background": "#FFFFFF",
                "text": "#2C3E50",
                "accent": "#FE4447"
            },
            "fonts": {"title": "Arial", "body": "Arial"},
            "style": "vibrant, energetic"
        },
        "elegant_dark": {
            "name": "优雅暗色",
            "colors": {
                "primary": "#D4AF37",
                "secondary": "#C0A030",
                "background": "#1A1A1A",
                "text": "#F4E4BC",
                "accent": "#D4AF37"
            },
            "fonts": {"title": "Georgia", "body": "Arial"},
            "style": "luxury, sophisticated"
        },
        "dark_tech": {
            "name": "暗黑科技",
            "colors": {
                "primary": "#00FF88",
                "secondary": "#00D4FF",
                "background": "#0A0A0A",
                "text": "#E0E0E0",
                "accent": "#00FF88"
            },
            "fonts": {"title": "Courier New", "body": "Arial"},
            "style": "cyberpunk, tech"
        },
        # ... 更多主题
    }

    def get_theme(self, theme_id: str) -> Dict[str, Any]:
        """获取主题配置"""
        return self.THEMES.get(theme_id, self.THEMES["modern_business"])

    def get_all_themes(self) -> Dict[str, Dict[str, Any]]:
        """获取所有主题"""
        return self.THEMES

    def recommend_theme(self, content_keywords: List[str]) -> str:
        """根据内容关键词推荐主题"""
        keyword_theme_map = {
            ["business", "corporate", "report"]: "modern_business",
            ["tech", "code", "programming"]: "dark_tech",
            ["academic", "research", "paper"]: "classic_blue",
            ["creative", "design", "art"]: "creative_colorful",
            ["anime", "game", "comic"]: "anime_cute",
        }

        content_lower = " ".join(content_keywords).lower()
        for keywords, theme in keyword_theme_map.items():
            if any(kw in content_lower for kw in keywords):
                return theme

        return "modern_business"
```

#### 4.5.5 PPTX 导出服务

**专业级 PPTX 导出 (pptx_export_service.py)**

```python
import io
from typing import Dict, Any
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

class PptxExportService:
    """专业级 PPTX 导出服务"""

    # 字体大小系统
    COVER_TITLE = Pt(48)      # 封面标题
    SECTION_TITLE = Pt(44)    # 章节标题
    SLIDE_TITLE = Pt(36)      # 幻灯片标题
    BODY = Pt(20)             # 正文

    # 行间距
    LINE_SPACING = 1.5

    # 18 种专业配色
    THEME_COLORS = {
        "modern_business": {
            "background": "FFFFFF",
            "title": "1E3A8A",
            "text": "1E293B",
            "accent": "3B82F6"
        },
        # ... 更多配色
    }

    def _hex_to_rgb(self, hex_color: str) -> RGBColor:
        """十六进制转 RGB"""
        hex_color = hex_color.lstrip('#')
        return RGBColor(
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16)
        )

    async def export_to_pptx(
        self,
        presentation_data: Dict[str, Any],
        theme: str = "modern_business"
    ) -> bytes:
        """导出为 PPTX 文件"""
        prs = Presentation()
        colors = self.THEME_COLORS.get(theme, self.THEME_COLORS["modern_business"])

        for slide_data in presentation_data.get("slides", []):
            self._create_slide(prs, slide_data, colors)

        output = io.BytesIO()
        prs.save(output)
        output.seek(0)
        return output.getvalue()

    def _create_slide(self, prs, slide_data, colors):
        """创建单个幻灯片"""
        layout = slide_data.get("layout", "bullet_points")

        if layout == "title_cover":
            self._add_title_slide(prs, slide_data, colors)
        elif layout == "bullet_points":
            self._add_content_slide(prs, slide_data, colors)
        # ... 更多布局处理
```

#### 4.5.6 API 端点清单

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| **基础 CRUD** |
| POST | `/api/v1/presentations` | 创建演示文稿 | 是 |
| GET | `/api/v1/presentations` | 获取文稿列表 | 是 |
| GET | `/api/v1/presentations/{id}` | 获取文稿详情 | 是 |
| PUT | `/api/v1/presentations/{id}` | 更新文稿 | 是 |
| DELETE | `/api/v1/presentations/{id}` | 删除文稿 | 是 |
| **AI 生成** |
| POST | `/api/v1/presentations/generate` | AI 生成演示文稿 | 是 |
| POST | `/api/v1/presentations/{id}/regenerate` | 重新生成 | 是 |
| **编辑功能** |
| POST | `/api/v1/presentations/{id}/theme` | 更换主题 | 是 |
| POST | `/api/v1/presentations/{id}/slides` | 添加幻灯片 | 是 |
| DELETE | `/api/v1/presentations/{id}/slides/{index}` | 删除幻灯片 | 是 |
| **导出** |
| GET | `/api/v1/presentations/{id}/export/html` | 导出 HTML | 是 |
| GET | `/api/v1/presentations/{id}/export/pptx` | 导出 PPTX | 是 |

---

### 4.6 Whisper Service (语音服务)

#### 4.6.1 服务概述

`whisper-service` 负责语音识别 (STT) 和语音合成 (TTS)。

**核心功能**：
- faster-whisper 语音识别
- edge-tts 语音合成
- 支持中英文

#### 4.6.2 项目结构

```
backend/whisper-service/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 应用入口
│   ├── config.py               # 配置管理
│   ├── services/               # 核心服务
│   │   ├── __init__.py
│   │   ├── whisper_service.py  # Whisper 识别
│   │   └── tts_service.py      # TTS 合成
│   └── api/v1/
│       ├── __init__.py
│       └── transcribe.py       # 语音 API
└── requirements.txt
```

#### 4.6.3 核心实现

```python
from faster_whisper import WhisperModel
import edge_tts

class WhisperService:
    """语音识别服务"""

    def __init__(self, model_size: str = "base"):
        self.model = WhisperModel(
            model_size,
            device="cpu",
            compute_type="int8"
        )

    async def transcribe(
        self,
        audio_bytes: bytes,
        language: str = "zh"
    ) -> str:
        """语音转文字"""
        segments, info = self.model.transcribe(
            audio_bytes,
            language=language,
            beam_size=5
        )
        return "".join([segment.text for segment in segments])

class TTSService:
    """语音合成服务"""

    async def synthesize(
        self,
        text: str,
        voice: str = "zh-CN-XiaoxiaoNeural"
    ) -> bytes:
        """文字转语音"""
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate="+0%"
        )

        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]

        return audio_data
```

---

*(第四部分完成 - 后端服务详解)*


## 五、前端架构详解

### 5.1 前端技术栈总览

| 技术类别 | 技术选型 | 版本 | 说明 |
|---------|---------|------|------|
| **框架** | Next.js | 16.1.1 | App Router, React Server Components |
| **UI 库** | shadcn/ui | latest | 基于 Radix UI + Tailwind CSS |
| **CSS 框架** | Tailwind CSS | 4.0 | 原子化 CSS, oklch 颜色空间 |
| **状态管理** | Zustand | 5.0.9 | 轻量级状态管理 |
| **HTTP 客户端** | Axios | 1.7.9 | 请求拦截器, 自动 Token 刷新 |
| **Markdown** | React Markdown | 9.0+ | Markdown 渲染, 代码高亮 |
| **代码高亮** | Prism.js / Shiki | - | 50+ 语言支持 |
| **类型检查** | TypeScript | 5.x | 类型安全 |

### 5.2 Next.js 14 项目结构

```
frontend-next/
├── src/
│   ├── app/                          # App Router 目录
│   │   ├── (auth)/                   # 认证路由组
│   │   │   ├── layout.tsx            # 认证布局 (无侧边栏)
│   │   │   ├── login/
│   │   │   │   └── page.tsx          # 登录页
│   │   │   └── register/
│   │   │       └── page.tsx          # 注册页
│   │   ├── (main)/                   # 主应用路由组
│   │   │   ├── layout.tsx            # 主布局 (侧边栏 + 认证保护)
│   │   │   ├── chat/                 # 聊天模块
│   │   │   │   ├── page.tsx          # 新会话页
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx      # 指定会话页
│   │   │   ├── documents/            # 文档管理
│   │   │   │   └── page.tsx
│   │   │   ├── presentations/        # 演示文稿
│   │   │   │   ├── page.tsx          # 列表页
│   │   │   │   ├── new/
│   │   │   │   │   └── page.tsx      # 创建页
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx      # 编辑器页
│   │   │   └── settings/             # 设置
│   │   │       └── page.tsx
│   │   ├── layout.tsx                # 根布局
│   │   ├── page.tsx                  # 首页 (重定向)
│   │   └── globals.css               # 全局样式
│   │
│   ├── components/                   # React 组件
│   │   ├── chat/                     # 聊天组件
│   │   │   ├── ChatContainer.tsx    # 聊天容器
│   │   │   ├── MessageList.tsx      # 消息列表
│   │   │   ├── MessageBubble.tsx    # 消息气泡
│   │   │   ├── InputArea.tsx        # 输入区域
│   │   │   ├── ToolCallPanel.tsx    # 工具调用面板
│   │   │   ├── CodeBlock.tsx        # 代码块
│   │   │   └── VoiceRecorder.tsx    # 语音录制
│   │   ├── sidebar/                  # 侧边栏组件
│   │   │   ├── Sidebar.tsx          # 侧边栏主组件
│   │   │   ├── ConversationList.tsx # 会话列表
│   │   │   └── ConversationItem.tsx # 会话项
│   │   ├── presentations/            # 演示文稿组件
│   │   │   ├── PresentationCard.tsx
│   │   │   ├── PresentationEditor.tsx
│   │   │   ├── SlideEditor.tsx
│   │   │   ├── SlidePreview.tsx
│   │   │   └── ThemeSelector.tsx
│   │   ├── documents/                # 文档组件
│   │   │   └── DocumentsPage.tsx
│   │   ├── ui/                       # shadcn/ui 基础组件
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── dialog.tsx
│   │   │   └── ...
│   │   └── providers/                # Context Provider
│   │       ├── AuthProvider.tsx     # 认证上下文
│   │       └── ThemeProvider.tsx    # 主题上下文
│   │
│   ├── lib/                          # 工具库
│   │   ├── api/                      # API 客户端
│   │   │   ├── client.ts             # Axios 实例
│   │   │   ├── auth.ts               # 认证 API
│   │   │   ├── chat.ts               # 聊天 API
│   │   │   ├── rag.ts                # RAG API
│   │   │   ├── voice.ts              # 语音 API
│   │   │   └── presentations.ts      # 演示文稿 API
│   │   ├── stores/                   # Zustand 状态管理
│   │   │   ├── authStore.ts          # 认证状态
│   │   │   ├── chatStore.ts          # 聊天状态
│   │   │   ├── settingsStore.ts      # 设置状态
│   │   │   └── presentationStore.ts  # 演示文稿状态
│   │   ├── types/                    # TypeScript 类型
│   │   │   ├── auth.ts
│   │   │   ├── chat.ts
│   │   │   └── presentations.ts
│   │   └── utils/                    # 工具函数
│   │       ├── markdown.ts           # Markdown 处理
│   │       └── format.ts             # 格式化工具
│   │
│   └── hooks/                        # React Hooks
│       ├── useSSE.ts                 # SSE 流式处理
│       └── useDebounce.ts            # 防抖 Hook
│
├── public/                           # 静态资源
├── tailwind.config.ts                # Tailwind 配置
├── next.config.ts                    # Next.js 配置
├── package.json                      # 依赖管理
└── tsconfig.json                     # TypeScript 配置
```

### 5.3 Next.js App Router 路由设计

#### 5.3.1 路由组 (Route Groups)

Next.js 14 使用路由组来组织代码，括号中的目录名不会出现在 URL 中：

```
app/
├── (auth)/           # 认证路由组 - 无侧边栏布局
│   ├── login/        → /login
│   └── register/     → /register
│
├── (main)/           # 主应用路由组 - 带侧边栏 + 认证保护
│   ├── chat/         → /chat
│   ├── documents/    → /documents
│   ├── presentations/→ /presentations
│   └── settings/     → /settings
│
└── page.tsx         → / (首页, 重定向到 /chat)
```

**路由组说明**:

| 路由组 | 用途 | 布局特点 | 认证要求 |
|--------|------|----------|---------|
| `(auth)` | 登录/注册 | 无侧边栏，居中卡片 | 公开 |
| `(main)` | 主应用 | 左侧边栏 + 主内容区 | 需要登录 |

#### 5.3.2 动态路由

```typescript
// app/(main)/chat/[id]/page.tsx
export default function ChatPage({ params }: { params: { id: string } }) {
  const conversationId = params.id;
  return <ChatContainer conversationId={conversationId} />;
}
```

**路由映射**:
- `/chat` → 新建会话
- `/chat/abc-123` → 加载 ID 为 `abc-123` 的会话
- `/presentations` → 演示文稿列表
- `/presentations/xyz-789` → 编辑 ID 为 `xyz-789` 的演示文稿

### 5.4 状态管理架构 (Zustand)

#### 5.4.1 authStore - 认证状态

```typescript
// lib/stores/authStore.ts

interface AuthState {
  // 状态
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  isInitialized: boolean;
  error: string | null;

  // 操作
  login: (email: string, password: string) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  refreshAccessToken: () => Promise<void>;
  clearError: () => void;
  initialize: () => Promise<void>;
}

// 持久化中间件 - Token 自动保存到 localStorage
const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      isInitialized: false,
      error: null,

      login: async (email, password) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authApiClient.login({ email, password });
          set({
            user: response.user,
            accessToken: response.access_token,
            refreshToken: response.refresh_token,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error: any) {
          set({
            error: error.response?.data?.detail || 'Login failed',
            isLoading: false,
          });
          throw error;
        }
      },

      logout: () => {
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
        });
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
      },

      refreshAccessToken: async () => {
        const { refreshToken } = get();
        if (!refreshToken) throw new Error('No refresh token');

        const response = await authApiClient.refreshToken({ refresh_token: refreshToken });
        set({
          accessToken: response.access_token,
          refreshToken: response.refresh_token || refreshToken, // 如果没返回新的则保持原值
        });
        localStorage.setItem('accessToken', response.access_token);
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
      }),
    }
  )
);
```

**认证流程图**:

```
用户登录
    │
    ▼
┌─────────────────┐
│  login() 调用    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  authApiClient.login()   │
│  POST /api/auth/login    │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  保存 Token 到 State     │
│  + localStorage          │
└────────┬────────────────┘
         │
         ▼
    跳转到 /chat
```

#### 5.4.2 chatStore - 聊天状态

```typescript
// lib/stores/chatStore.ts

interface ChatState {
  // 状态
  conversations: Conversation[];
  currentConversationId: string | null;
  messages: Record<string, Message[]>; // { conversationId: messages[] }
  isStreaming: boolean;
  currentToolCalls: ToolCall[];
  error: string | null;

  // 操作
  fetchConversations: () => Promise<void>;
  createConversation: () => Promise<string>;
  deleteConversation: (id: string) => Promise<void>;
  selectConversation: (id: string) => Promise<void>;
  sendMessage: (content: string, images?: string[]) => Promise<void>;
  stopStreaming: () => void;
  clearMessages: (conversationId: string) => void;
}

const useChatStore = create<ChatState>()((set, get) => ({
  conversations: [],
  currentConversationId: null,
  messages: {},
  isStreaming: false,
  currentToolCalls: [],
  error: null,

  sendMessage: async (content, images) => {
    const { currentConversationId } = get();
    let conversationId = currentConversationId;

    // 如果没有当前会话，创建新会话
    if (!conversationId) {
      conversationId = await get().createConversation();
    }

    // 添加用户消息
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content,
      images,
      timestamp: new Date(),
    };

    set((state) => ({
      messages: {
        ...state.messages,
        [conversationId]: [...(state.messages[conversationId] || []), userMessage],
      },
      isStreaming: true,
    }));

    // 发送到后端 (SSE 流式)
    await streamChat(conversationId, content, images, {
      onText: (delta) => { /* 追加 AI 回复 */ },
      onToolStart: (tool) => { /* 工具开始 */ },
      onToolEnd: (tool) => { /* 工具结束 */ },
      onDone: () => { set({ isStreaming: false }); },
    });
  },

  stopStreaming: () => {
    // 停止当前 SSE 流
    stopCurrentChat();
    set({ isStreaming: false });
  },
}));
```

**消息流向图**:

```
用户输入消息
    │
    ▼
InputArea 组件
    │
    ▼
chatStore.sendMessage()
    │
    ├─→ 创建/获取会话
    │
    ├─→ 添加用户消息到 State
    │
    └─→ chatApiClient.streamChat()
            │
            ▼
        SSE 流式响应
            │
            ├─→ onText: 追加 AI 回复
            ├─→ onToolStart: 显示工具执行中
            ├─→ onToolEnd: 显示工具结果
            └─→ onDone: 完成流式
```

### 5.5 API 客户端层设计

#### 5.5.1 Axios 实例配置

```typescript
// lib/api/client.ts

import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { useAuthStore } from '@/stores/authStore';

// 创建 Axios 实例
export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || '',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 - 自动携带 Token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const accessToken = localStorage.getItem('accessToken');
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器 - 自动刷新 Token
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry: boolean;
    };

    // 401 错误且未重试过
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // 刷新 Token
        const authStore = useAuthStore.getState();
        await authStore.refreshAccessToken();

        // 重试原请求
        const newAccessToken = localStorage.getItem('accessToken');
        if (newAccessToken) {
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        // 刷新失败，登出
        const authStore = useAuthStore.getState();
        authStore.logout();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);
```

**拦截器工作流程**:

```
请求发送
    │
    ▼
请求拦截器
    │
    ├─→ 从 localStorage 读取 accessToken
    │
    └─→ 添加 Authorization: Bearer <token>
         │
         ▼
    发送请求
         │
         ▼
    响应拦截器
         │
    ├─→ 成功 → 返回响应
    │
    └─→ 401 错误
         │
         ├─→ 调用 refreshAccessToken()
         │
         ├─→ 更新 localStorage
         │
         └─→ 重试原请求
                  │
                  ├─→ 成功 → 返回响应
                  │
                  └─→ 失败 → 登出 → 跳转 /login
```

#### 5.5.2 SSE 流式处理

```typescript
// lib/api/chat.ts

export async function streamChat(
  conversationId: string,
  content: string,
  images?: string[],
  callbacks: {
    onText?: (delta: string) => void;
    onToolStart?: (tool: ToolCallStart) => void;
    onToolEnd?: (tool: ToolCallEnd) => void;
    onCitation?: (citation: Citation) => void;
    onDone?: (finalMessage: string) => void;
    onError?: (error: string) => void;
  }
) {
  const response = await fetch('/api/chat/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
    },
    body: JSON.stringify({ conversation_id: conversationId, content, images }),
  });

  if (!response.ok) {
    throw new Error('Failed to connect');
  }

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  if (!reader) {
    callbacks.onError?.('No response body');
    return;
  }

  let buffer = '';
  let fullContent = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const data = JSON.parse(line.slice(6));
          const event = data.event;

          switch (event) {
            case 'text':
              fullContent += data.data.content;
              callbacks.onText?.(data.data.content);
              break;

            case 'tool_start':
              callbacks.onToolStart?.({
                toolName: data.data.tool_name,
                toolId: data.data.tool_id,
              });
              break;

            case 'tool_end':
              callbacks.onToolEnd?.({
                toolId: data.data.tool_id,
                output: data.data.output,
                duration: data.data.duration,
              });
              break;

            case 'citation':
              callbacks.onCitation?.(data.data);
              break;

            case 'done':
              callbacks.onDone?.(fullContent);
              break;

            case 'error':
              callbacks.onError?.(data.data.message);
              break;
          }
        } catch (e) {
          console.error('Failed to parse SSE data:', e);
        }
      }
    }
  }
}
```

### 5.6 组件架构详解

#### 5.6.1 ChatContainer - 聊天容器

```typescript
// components/chat/ChatContainer.tsx

export function ChatContainer() {
  const { currentConversationId, messages, isStreaming } = useChatStore();
  const { isAuthenticated } = useAuthStore();

  // 检查会话 ID
  const params = useParams();
  const conversationId = params.id || currentConversationId;

  const currentMessages = messages[conversationId] || [];

  return (
    <div className="flex h-screen">
      {/* 左侧边栏在 (main)/layout.tsx 中 */}

      {/* 主聊天区域 */}
      <main className="flex-1 flex flex-col">
        <MessageList
          messages={currentMessages}
          isStreaming={isStreaming}
          conversationId={conversationId}
        />
        <InputArea
          onSend={(content, images) => handleSend(conversationId, content, images)}
          onStop={() => stopStreaming()}
          isStreaming={isStreaming}
        />
      </main>
    </div>
  );
}
```

#### 5.6.2 MessageBubble - 消息气泡

```typescript
// components/chat/MessageBubble.tsx

interface MessageBubbleProps {
  message: Message;
  isStreaming?: boolean;
  onRegenerate?: () => void;
  onCopy?: () => void;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  images?: string[];      // Base64 图片
  toolCalls?: ToolCall[]; // 工具调用记录
  citations?: Citation[]; // 引用来源
}

export function MessageBubble({ message, isStreaming = false }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <div className={cn('flex', isUser ? 'justify-end' : 'justify-start')}>
      <div className={cn(
        'max-w-[80%] rounded-2xl px-4 py-2',
        isUser
          ? 'bg-primary text-primary-foreground'
          : 'bg-muted'
      )}>
        {/* 用户消息 */}
        {isUser ? (
          <div className="whitespace-pre-wrap">{message.content}</div>
        ) : (
          /* AI 消息 - Markdown 渲染 */
          <>
            <ReactMarkdown
              components={{
                p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                ul: ({ children }) => <ul className="list-disc list-inside mb-2">{children}</ul>,
                ol: ({ children }) => <ol className="list-decimal list-inside mb-2">{children}</ol>,
                code: ({ inline, className, children }) => {
                  const language = className?.replace('language-', '') || 'plaintext';
                  return inline ? (
                    <code className="bg-muted rounded px-1 py-0.5 text-sm">{children}</code>
                  ) : (
                    <CodeBlock code={String(children)} language={language} />
                  );
                },
              }}
            >
              {message.content}
            </ReactMarkdown>

            {/* 工具调用面板 */}
            {message.toolCalls && message.toolCalls.length > 0 && (
              <ToolCallPanel toolCalls={message.toolCalls} />
            )}

            {/* 引用展示 */}
            {message.citations && message.citations.length > 0 && (
              <CitationPanel citations={message.citations} />
            )}
          </>
        )}

        {/* 图片展示 */}
        {message.images && message.images.map((img, i) => (
          <img key={i} src={`data:image/jpeg;base64,${img}`} alt="上传的图片" />
        ))}
      </div>
    </div>
  );
}
```

#### 5.6.3 InputArea - 输入区域

```typescript
// components/chat/InputArea.tsx

interface InputAreaProps {
  onSend: (content: string, images?: string[]) => void;
  onStop: () => void;
  isStreaming?: boolean;
  disabled?: boolean;
}

export function InputArea({ onSend, onStop, isStreaming = false, disabled = false }: InputAreaProps) {
  const [input, setInput] = useState('');
  const [images, setImages] = useState<{ file: File; preview: string }[]>([]);

  // 处理发送
  const handleSubmit = () => {
    if (!input.trim() && images.length === 0) return;

    const imageBase64s = images.map((img) => img.preview.split(',')[1]);
    onSend(input.trim(), imageBase64s.length > 0 ? imageBase64s : undefined);

    setInput('');
    setImages([]);
  };

  // 处理粘贴图片
  const handlePaste = (e: React.ClipboardEvent) => {
    const items = e.clipboardData?.items;
    if (!items) return;

    for (const item of items) {
      if (item.type.startsWith('image/')) {
        const file = item.getAsFile();
        if (file) {
          const reader = new FileReader();
          reader.onload = (event) => {
            setImages((prev) => [...prev, {
              file,
              preview: event.target?.result as string,
            }]);
          };
          reader.readAsDataURL(file);
        }
      }
    }
  };

  // 处理键盘快捷键
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="border-t bg-background p-4">
      {/* 图片预览区 */}
      {images.length > 0 && (
        <div className="mb-3 flex flex-wrap gap-2">
          {images.map((img, index) => (
            <div key={index} className="relative group">
              <img
                src={img.preview}
                alt="预览"
                className="h-20 w-20 rounded-lg object-cover border"
              />
              <button
                onClick={() => removeImage(index)}
                className="absolute -right-2 -top-2 rounded-full bg-destructive p-1 opacity-0 group-hover:opacity-100"
              >
                <X className="h-3 w-3 text-destructive-foreground" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* 输入框 */}
      <Textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        onPaste={handlePaste}
        placeholder="输入消息... (Shift+Enter 换行)"
        disabled={disabled || isStreaming}
        className="min-h-[60px] resize-none"
        autoFocus
      />

      {/* 底部工具栏 */}
      <div className="mt-2 flex items-center justify-between">
        <div className="flex gap-2">
          {/* 图片上传按钮 */}
          <Button variant="ghost" size="icon" asChild>
            <label className="cursor-pointer">
              <ImageIcon className="h-5 w-5" />
              <input
                type="file"
                accept="image/*"
                multiple
                className="hidden"
                onChange={(e) => handleImageUpload(e.target.files)}
              />
            </label>
          </Button>

          {/* 语音录制按钮 */}
          <VoiceRecorder onTranscript={(text) => setInput((prev) => prev + text)} />
        </div>

        <div className="flex gap-2">
          {isStreaming ? (
            <Button onClick={onStop} variant="destructive">
              <Square className="h-4 w-4 mr-2" />
              停止生成
            </Button>
          ) : (
            <Button onClick={handleSubmit} disabled={!input.trim() && images.length === 0}>
              <Send className="h-4 w-4 mr-2" />
              发送
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
```

#### 5.6.4 ToolCallPanel - 工具调用面板

```typescript
// components/chat/ToolCallPanel.tsx

interface ToolCall {
  id: string;
  name: string;
  args: Record<string, any>;
  status: 'running' | 'success' | 'error';
  output?: string;
  duration?: number;
}

const toolIcons: Record<string, React.ComponentType<{ className?: string }>> = {
  search_engine: Search,
  scrape: Globe,
  execute_python_code: Code,
  analyze_csv_data: Database,
  generate_presentation: FileText,
  rag_search: Database,
  default: Terminal,
};

export function ToolCallPanel({ toolCalls }: { toolCalls: ToolCall[] }) {
  const [isExpanded, setIsExpanded] = useState(true);

  return (
    <div className="rounded-lg border bg-muted/50">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex w-full items-center justify-between p-3"
      >
        <span className="text-sm font-medium">
          工具调用 ({toolCalls.length})
        </span>
        {isExpanded ? <ChevronUp /> : <ChevronDown />}
      </button>

      {isExpanded && (
        <div className="border-t p-3 space-y-2">
          {toolCalls.map((toolCall) => (
            <ToolCallItem key={toolCall.id} toolCall={toolCall} />
          ))}
        </div>
      )}
    </div>
  );
}

function ToolCallItem({ toolCall }: { toolCall: ToolCall }) {
  const Icon = toolIcons[toolCall.name] || toolIcons.default;

  // 状态样式
  const statusStyles = {
    running: 'border-blue-500/30 bg-blue-500/10',
    success: 'border-green-500/30 bg-green-500/10',
    error: 'border-red-500/30 bg-red-500/10',
  };

  // 状态图标
  const statusIcon = {
    running: <Loader2 className="h-3 w-3 animate-spin text-blue-500" />,
    success: <CheckCircle className="h-3 w-3 text-green-500" />,
    error: <XCircle className="h-3 w-3 text-red-500" />,
  };

  // 提取图片
  const hasImage = toolCall.output?.includes('[IMAGE_BASE64:');
  const imageMatch = toolCall.output?.match(/\[IMAGE_BASE64:([^\]]+)\]/);
  const imageData = imageMatch?.[1];

  // 提取演示文稿
  const hasPresentation = toolCall.output?.includes('[PRESENTATION_HTML:]');
  const presentationMatch = toolCall.output?.match(/\[PRESENTATION_HTML:([^\]]+)\]/);
  const presentationData = presentationMatch?.[1];

  return (
    <div className={cn('rounded-lg border p-3', statusStyles[toolCall.status])}>
      <div className="flex items-center gap-2">
        <Icon className="h-4 w-4" />
        <span className="font-medium">{displayName}</span>
        {statusIcon[toolCall.status]}
        {toolCall.duration && (
          <span className="text-xs text-muted-foreground">{toolCall.duration.toFixed(1)}s</span>
        )}
      </div>

      {/* 工具输出 */}
      {toolCall.output && (
        <div className="mt-2 text-sm text-muted-foreground">
          <OutputExtractor content={toolCall.output} />
        </div>
      )}

      {/* 图片展示 */}
      {hasImage && imageData && (
        <img
          src={`data:image/png;base64,${imageData}`}
          alt="工具生成的图片"
          className="mt-2 rounded-lg border"
        />
      )}

      {/* PPT 预览 */}
      {hasPresentation && presentationData && (
        <PresentationPreview htmlData={presentationData} />
      )}
    </div>
  );
}
```

### 5.7 Tailwind CSS 4.0 主题系统

#### 5.7.1 全局样式配置

```css
/* app/globals.css */

@import "tailwindcss";
@import "tw-animate-css";

/* 自定义暗黑模式变体 */
@custom-variant dark (&:is(.dark *));

/* 内联主题配置 */
@theme inline {
  /* 颜色变量映射 */
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);

  /* 字体变量 */
  --font-sans: var(--font-geist-sans);
  --font-mono: var(--font-geist-mono);
}

/* 根变量 - 亮色模式 */
:root {
  /* 半径 */
  --radius: 0.625rem;

  /* 颜色 - oklch 空间 */
  --background: oklch(1 0 0);              /* 纯白 */
  --foreground: oklch(0.145 0 0);          /* 深灰 */

  --primary: oklch(0.205 0 0);              /* 主色 */
  --primary-foreground: oklch(0.985 0 0);  /* 主色前景 */

  --secondary: oklch(0.961 0.006 240.4);
  --secondary-foreground: oklch(0.205 0 0);

  --muted: oklch(0.961 0.006 240.4);
  --muted-foreground: oklch(0.504 0 0);

  --accent: oklch(0.961 0.006 240.4);
  --accent-foreground: oklch(0.205 0 0);

  --destructive: oklch(0.577 0.245 27.9);
  --destructive-foreground: oklch(0.985 0 0);

  --border: oklch(0.902 0 0);
  --input: oklch(0.902 0 0);
  --ring: oklch(0.708 0 0);

  /* 卡片 */
  --card: oklch(1 0 0);
  --card-foreground: oklch(0.145 0 0);

  /* 弹窗 */
  --popover: oklch(1 0 0);
  --popover-foreground: oklch(0.145 0 0);
}

/* 暗色模式 */
.dark {
  --background: oklch(0.145 0 0);          /* 深黑 */
  --foreground: oklch(0.985 0 0);          /* 灰白 */

  --primary: oklch(0.922 0 0);              /* 主色 */
  --primary-foreground: oklch(0.205 0 0);  /* 主色前景 */

  --secondary: oklch(0.205 0 0);
  --secondary-foreground: oklch(0.961 0.006 240.4);

  --muted: oklch(0.205 0 0);
  --muted-foreground: oklch(0.596 0 0);

  --accent: oklch(0.205 0 0);
  --accent-foreground: oklch(0.961 0.006 240.4);

  --destructive: oklch(0.627 0.265 27.9);
  --destructive-foreground: oklch(0.985 0 0);

  --border: oklch(0.267 0 0);
  --input: oklch(0.267 0 0);
  --ring: oklch(0.439 0 0);

  --card: oklch(0.205 0 0);
  --card-foreground: oklch(0.985 0 0);

  --popover: oklch(0.205 0 0);
  --popover-foreground: oklch(0.985 0 0);
}

/* 基础层样式 */
@layer base {
  * {
    @apply border-border outline-ring/50;
  }

  body {
    @apply bg-background text-foreground;
    font-feature-settings: "rlig" 1, "calt" 1;
  }

  /* 滚动条样式 */
  ::-webkit-scrollbar {
    @apply w-2;
  }

  ::-webkit-scrollbar-track {
    @apply bg-muted;
  }

  ::-webkit-scrollbar-thumb {
    @apply bg-muted-foreground/50 rounded-full;
  }

  ::-webkit-scrollbar-thumb:hover {
    @apply bg-muted-foreground/70;
  }
}
```

#### 5.7.2 主题切换机制

```typescript
// components/providers/ThemeProvider.tsx

type Theme = 'dark' | 'light' | 'system';

interface ThemeProviderProps {
  children: React.ReactNode;
  defaultTheme?: Theme;
}

export function ThemeProvider({ children, defaultTheme = 'system' }: ThemeProviderProps) {
  const [theme, setTheme] = useState<Theme>(defaultTheme);

  useEffect(() => {
    // 从 localStorage 读取保存的主题
    const stored = localStorage.getItem('theme') as Theme;
    if (stored) {
      setTheme(stored);
    }
  }, []);

  useEffect(() => {
    const root = window.document.documentElement;
    root.classList.remove('light', 'dark');

    if (theme === 'system') {
      // 跟随系统主题
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches
        ? 'dark'
        : 'light';
      root.classList.add(systemTheme);
    } else {
      root.classList.add(theme);
    }
  }, [theme]);

  const value = {
    theme,
    setTheme: (theme: Theme) => {
      setTheme(theme);
      localStorage.setItem('theme', theme);
    },
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}
```

### 5.8 认证流程详解

#### 5.8.1 AuthProvider - 认证上下文

```typescript
// components/providers/AuthProvider.tsx

const publicRoutes = ['/login', '/register', '/'];

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isInitialized, setIsInitialized] = useState(false);
  const { isAuthenticated, accessToken } = useAuthStore();
  const router = useRouter();
  const pathname = usePathname();

  // 初始化 - 从 localStorage 恢复 Token
  useEffect(() => {
    const storedToken = localStorage.getItem('accessToken');
    const storedRefreshToken = localStorage.getItem('refreshToken');

    if (storedToken && !isAuthenticated) {
      useAuthStore.setState({
        accessToken: storedToken,
        refreshToken: storedRefreshToken,
        isAuthenticated: true,
      });
    }

    setIsInitialized(true);
  }, []);

  // 路由保护
  useEffect(() => {
    if (!isInitialized) return;

    const isPublicRoute = publicRoutes.some((route) => pathname === route);

    // 未登录且访问受保护路由 → 重定向到登录页
    if (!isAuthenticated && !isPublicRoute) {
      router.push('/login');
    }
    // 已登录且访问登录/注册页 → 重定向到聊天页
    else if (isAuthenticated && (pathname === '/login' || pathname === '/register')) {
      router.push('/chat');
    }
  }, [isAuthenticated, pathname, router, isInitialized]);

  if (!isInitialized) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  return <AuthContext.Provider value={{ isInitialized }}>{children}</AuthContext.Provider>;
}
```

#### 5.8.2 登录页面实现

```typescript
// app/(auth)/login/page.tsx

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/authStore';
import { Button, Input, Card, CardHeader, CardTitle, CardDescription } from '@/components/ui';

export default function LoginPage() {
  const router = useRouter();
  const { login, isLoading, error, clearError } = useAuthStore();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();

    try {
      await login(email, password);
      // 登录成功后路由保护会自动跳转到 /chat
    } catch {
      // 错误已在 store 中处理
    }
  };

  return (
    <div className="flex h-screen items-center justify-center bg-background">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold">Welcome Back</CardTitle>
          <CardDescription>
            Enter your credentials to access Stream-Agent
          </CardDescription>
        </CardHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={isLoading}
            />
            <div className="relative">
              <Input
                type={showPassword ? 'text' : 'password'}
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={isLoading}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2"
              >
                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
          </div>

          {error && (
            <div className="rounded-md bg-destructive/15 p-3 text-sm text-destructive">
              {error}
            </div>
          )}

          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Signing in...
              </>
            ) : (
              'Sign In'
            )}
          </Button>

          <div className="text-center text-sm">
            <span className="text-muted-foreground">Don't have an account? </span>
            <button
              type="button"
              onClick={() => router.push('/register')}
              className="underline hover:text-primary"
            >
              Sign up
            </button>
          </div>
        </form>
      </Card>
    </div>
  );
}
```

### 5.9 页面布局详解

#### 5.9.1 根布局

```typescript
// app/layout.tsx

import type { Metadata } from 'next';
import { GeistMono, GeistSans } from 'geist/font';
import './globals.css';

export const metadata: Metadata = {
  title: 'Stream-Agent V9',
  description: 'AI Research Assistant powered by LangChain',
};

const geistSans = GeistSans({
  subsets: ['latin'],
  variable: '--font-geist-sans',
});

const geistMono = GeistMono({
  subsets: ['latin'],
  variable: '--font-geist-mono',
});

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable}`}
        suppressHydrationWarning
      >
        <ThemeProvider>
          <AuthProvider>
            {children}
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
```

#### 5.9.2 主应用布局

```typescript
// app/(main)/layout.tsx

import { Sidebar } from '@/components/sidebar/Sidebar';

export default function MainLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* 左侧边栏 */}
      <Sidebar />

      {/* 主内容区 */}
      <main className="flex-1 overflow-y-auto">
        <div className="h-full">
          {children}
        </div>
      </main>
    </div>
  );
}
```

#### 5.9.3 认证布局

```typescript
// app/(auth)/layout.tsx

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-muted/40">
      {children}
    </div>
  );
}
```

### 5.10 SSE 流式响应处理

```typescript
// hooks/useSSE.ts

interface SSEOptions {
  onMessage?: (data: any) => void;
  onError?: (error: string) => void;
  onComplete?: () => void;
}

export function useSSE(url: string, options: SSEOptions) {
  const [isConnected, setIsConnected] = useState(false);
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const eventSource = new EventSource(url, {
      withCredentials: true,
    });

    eventSource.onopen = () => {
      setIsConnected(true);
      setError(null);
    };

    eventSource.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data);
        setData(parsed);
        options.onMessage?.(parsed);
      } catch (e) {
        console.error('Failed to parse SSE data:', e);
      }
    };

    eventSource.onerror = (error) => {
      setIsConnected(false);
      const errorMsg = 'Connection lost';
      setError(errorMsg);
      options.onError?.(errorMsg);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [url]);

  return { isConnected, data, error };
}
```

---

## 六、开发环境配置

### 6.1 环境要求

#### 6.1.1 必需软件

| 软件 | 版本要求 | 用途 | 下载地址 |
|------|---------|------|----------|
| **Python** | 3.10+ | 后端运行时 | https://www.python.org/downloads/ |
| **Node.js** | 18+ | 前端运行时 | https://nodejs.org/ |
| **Git** | 最新版 | 版本控制 | https://git-scm.com/downloads |
| **PostgreSQL** | 15+ (可选) | 生产数据库 | https://www.postgresql.org/download/ |
| **Conda** | 最新版 (推荐) | 环境管理 | https://www.anaconda.com/download |

#### 6.1.2 可选服务

| 服务 | 版本 | 用途 | 何时需要 |
|------|------|------|----------|
| **Supabase** | - | 云数据库 + pgvector | 云端部署 |
| **Redis** | 7+ | 缓存/会话存储 | 高并发场景 |
| **MinIO** | 最新版 | 对象存储 | 本地文件存储 |

#### 6.1.3 Python 依赖版本总览

```
核心框架:
- fastapi >= 0.115.0
- uvicorn >= 0.30.0
- pydantic >= 2.0.0

数据库:
- sqlalchemy >= 2.0.0
- aiosqlite >= 0.20.0       # SQLite 异步驱动
- psycopg2-binary >= 2.9.9  # PostgreSQL 驱动
- asyncpg >= 0.29.0         # PostgreSQL 异步驱动

向量存储:
- pgvector >= 0.3.0         # PostgreSQL pgvector 扩展
- pymilvus >= 2.4.0         # Milvus 客户端 (可选)

AI/ML:
- langchain >= 0.3.0
- langgraph >= 0.2.0
- langchain-google-genai >= 2.0.0
- langchain-openai >= 0.2.0
- sentence-transformers >= 2.7.0  # Embedding
- e2b-code-interpreter >= 1.0.0    # 代码执行

工具:
- python-jose[cryptography] >= 3.3.0  # JWT
- bcrypt >= 4.0.0                      # 密码加密
- httpx >= 0.27.0                       # HTTP 客户端
- PyPDF2 >= 3.0.0                       # PDF 解析
- python-pptx >= 0.6.21                 # PPTX 导出
- Pillow >= 10.0.0                      # 图片处理
```

#### 6.1.4 前端依赖版本总览

```
核心框架:
- next: 16.1.1
- react: 19.2.3
- react-dom: 19.2.3

UI 组件:
- @radix-ui/*: 各种 UI 基础组件
- lucide-react: 0.562.0 (图标库)
- class-variance-authority: 0.7.1
- clsx: 2.1.1
- tailwind-merge: 3.4.0

样式:
- tailwindcss: 4.0
- @tailwindcss/postcss: 4
- tw-animate-css: 1.4.0

状态管理:
- zustand: 5.0.9

HTTP 客户端:
- axios: 1.13.2

Markdown 渲染:
- react-markdown: 10.1.0
- rehype-highlight: 7.0.2
- remark-gfm: 4.0.1
```

### 6.2 项目克隆

```bash
# 克隆项目
git clone https://github.com/your-username/My-Chat-LangChain.git
cd My-Chat-LangChain

# 或使用 SSH
git clone git@github.com:your-username/My-Chat-LangChain.git
cd My-Chat-LangChain
```

### 6.3 Conda 环境配置 (推荐)

#### 6.3.1 创建 Conda 环境

```bash
# 创建 Python 3.10 环境
conda create -n My-Chat-LangChain python=3.10 -y

# 激活环境
conda activate My-Chat-LangChain

# 验证 Python 版本
python --version  # 应显示 Python 3.10.x
```

#### 6.3.2 配置 pip 镜像 (可选，加速下载)

```bash
# 临时使用清华镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple package-name

# 永久配置
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### 6.4 后端服务配置

#### 6.4.1 安装依赖

```bash
# 激活 Conda 环境
conda activate My-Chat-LangChain

# 进入各服务目录安装依赖

# Auth Service
cd backend/auth-service
pip install -r requirements.txt

# Chat Service
cd ../chat-service
pip install -r requirements.txt

# RAG Service
cd ../rag-service
pip install -r requirements.txt

# Presentation Service
cd ../presentation-service
pip install -r requirements.txt

# Whisper Service (可选)
cd ../whisper-service
pip install -r requirements.txt

# 返回项目根目录
cd ../../
```

#### 6.4.2 配置环境变量

**各服务的 .env 文件配置**:

```bash
# 1. Auth Service
cd backend/auth-service
cp .env.example .env
# 编辑 .env 文件，修改 JWT_SECRET 等

# 2. Chat Service
cd ../chat-service
cp .env.example .env
# 必需配置: GOOGLE_API_KEY 或 OPENAI_API_KEY

# 3. RAG Service
cd ../rag-service
cp .env.example .env
# 配置 DATABASE_URL (SQLite 或 PostgreSQL)

# 4. Presentation Service
cd ../presentation-service
cp .env.example .env
# 必需配置: GOOGLE_API_KEY 或 OPENAI_API_KEY

# 5. Whisper Service (可选)
cd ../whisper-service
cp .env.example .env
```

**关键环境变量说明**:

| 变量名 | 服务 | 必需 | 说明 |
|--------|------|------|------|
| `JWT_SECRET` | 全部 | 是 | JWT 签名密钥 (至少 32 字符) |
| `GOOGLE_API_KEY` | chat, presentation | 是* | Gemini API Key |
| `OPENAI_API_KEY` | chat, presentation | 是* | OpenAI/兼容 API Key |
| `DATABASE_URL` | 全部 | 否 | 默认使用 SQLite |
| `E2B_API_KEY` | chat, presentation | 否 | 代码执行功能 |
| `BRIGHT_DATA_API_KEY` | chat | 否 | MCP 工具 |

\* 至少配置一个 LLM 提供商

#### 6.4.3 数据库初始化

**SQLite (开发/测试)**:

```bash
# SQLite 会自动创建数据库文件
# 首次运行服务时会自动初始化表结构

# 数据库文件位置:
# - auth-service: ./auth.db
# - chat-service: ./chat.db
# - rag-service: ./rag_test.db
# - presentation-service: ./presentations.db
```

**PostgreSQL (生产环境)**:

```bash
# 1. 安装 PostgreSQL
# Windows: 下载安装程序
# Linux: sudo apt install postgresql postgresql-contrib

# 2. 创建数据库和用户
psql -U postgres
CREATE USER streamagent WITH PASSWORD 'your_password';
CREATE DATABASE auth_db OWNER streamagent;
CREATE DATABASE chat_db OWNER streamagent;
CREATE DATABASE rag_db OWNER streamagent;
CREATE DATABASE presentation_db OWNER streamagent;
GRANT ALL PRIVILEGES ON DATABASE auth_db, chat_db, rag_db, presentation_db TO streamagent;
\q

# 3. 启用 pgvector 扩展 (rag_db)
psql -U postgres -d rag_db
CREATE EXTENSION IF NOT EXISTS vector;
\q

# 4. 更新 .env 文件
DATABASE_URL=postgresql+asyncpg://streamagent:your_password@localhost:5432/auth_db
```

**Supabase (云端)**:

```bash
# 1. 注册 Supabase 账号: https://supabase.com
# 2. 创建新项目
# 3. 获取连接信息 (Settings > Database)
# 4. 启用 pgvector 扩展 (Database > Extensions > pgvector > Enable)

# 更新 .env
DATABASE_URL=postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
```

### 6.5 前端配置

#### 6.5.1 安装依赖

```bash
cd frontend-next

# 使用 npm 安装
npm install

# 或使用 pnpm (更快)
pnpm install

# 或使用 yarn
yarn install
```

#### 6.5.2 配置环境变量

```bash
# 创建环境变量文件
cp .env.example .env.local

# 编辑 .env.local
```

**.env.local 配置示例**:

```bash
# API 服务地址 (本地开发)
NEXT_PUBLIC_API_URL=http://localhost:8002
NEXT_PUBLIC_AUTH_URL=http://localhost:8001
NEXT_PUBLIC_RAG_URL=http://localhost:8004
NEXT_PUBLIC_PRESENTATION_URL=http://localhost:8005
NEXT_PUBLIC_WHISPER_URL=http://localhost:8003

# 生产环境示例
# NEXT_PUBLIC_API_URL=https://chat-service-xxx.onrender.com
# NEXT_PUBLIC_AUTH_URL=https://auth-service-xxx.onrender.com
# NEXT_PUBLIC_RAG_URL=https://rag-service-xxx.onrender.com
```

#### 6.5.3 配置 Next.js Rewrites (可选)

如果遇到代理拦截问题，可在 `next.config.ts` 中配置 rewrites:

```typescript
// next.config.ts
import type { NextConfig } from "next";

const config: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/v1/auth/:path*",
        destination: "http://127.0.0.1:8001/api/v1/auth/:path*",
      },
      {
        source: "/api/v1/chat/:path*",
        destination: "http://127.0.0.1:8002/api/v1/chat/:path*",
      },
      {
        source: "/api/v1/rag/:path*",
        destination: "http://127.0.0.1:8004/api/v1/rag/:path*",
      },
      {
        source: "/api/v1/presentations/:path*",
        destination: "http://127.0.0.1:8005/api/v1/presentations/:path*",
      },
    ];
  },
};

export default config;
```

### 6.6 开发工具配置

#### 6.6.1 VS Code 推荐扩展

| 扩展名 | 用途 |
|--------|------|
| Python | Python 语言支持 |
| Pylance | Python 类型检查 |
| ESLint | JavaScript/TypeScript 代码检查 |
| Prettier | 代码格式化 |
| Tailwind CSS IntelliSense | Tailwind 类名自动补全 |
| Auto Rename Tag | HTML 标签同步重命名 |
| Error Lens | 内联错误显示 |
| GitLens | Git 增强 |

#### 6.6.2 VS Code 工作区配置

创建 `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "A:\\Anaconda\\envs\\My-Chat-LangChain\\python.exe",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "tailwindCSS.experimental.classRegex": [
    ["cva\\(([^)]*)\\)", "[\"'`]([^\"'`]*).*?[\"'`]"]
  ],
  "files.associations": {
    "*.env": "dotenv"
  }
}
```

#### 6.6.3 Git 配置

```bash
# 配置用户信息
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 配置 .gitignore
# 项目已包含 .gitignore，无需额外配置
```

### 6.7 启动开发服务

#### 6.7.1 方式一：手动启动各服务

**打开 5 个终端窗口**:

```bash
# 终端 1: Auth Service
conda activate My-Chat-LangChain
cd backend/auth-service
uvicorn app.main:app --port 8001 --reload

# 终端 2: Chat Service
conda activate My-Chat-LangChain
cd backend/chat-service
uvicorn app.main:app --port 8002 --reload

# 终端 3: RAG Service
conda activate My-Chat-LangChain
cd backend/rag-service
uvicorn app.main:app --port 8004 --reload

# 终端 4: Presentation Service
conda activate My-Chat-LangChain
cd backend/presentation-service
uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload

# 终端 5: Frontend
cd frontend-next
npm run dev
```

#### 6.7.2 方式二：使用启动脚本

**Windows (PowerShell)**:

创建 `start-dev.ps1`:

```powershell
# 启动开发环境

$env:PYTHONPATH = "A:\Anaconda\envs\My-Chat-LangChain\python.exe"

# 启动后端服务 (在后台)
Start-Process -NoNewWindow -FilePath "A:\Anaconda\envs\My-Chat-LangChain\python.exe" -ArgumentList "-m", "uvicorn", "app.main:app", "--port", "8001", "--reload" -WorkingDirectory "backend\auth-service"
Start-Process -NoNewWindow -FilePath "A:\Anaconda\envs\My-Chat-LangChain\python.exe" -ArgumentList "-m", "uvicorn", "app.main:app", "--port", "8002", "--reload" -WorkingDirectory "backend\chat-service"
Start-Process -NoNewWindow -FilePath "A:\Anaconda\envs\My-Chat-LangChain\python.exe" -ArgumentList "-m", "uvicorn", "app.main:app", "--port", "8004", "--reload" -WorkingDirectory "backend\rag-service"
Start-Process -NoNewWindow -FilePath "A:\Anaconda\envs\My-Chat-LangChain\python.exe" -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8005", "--reload" -WorkingDirectory "backend\presentation-service"

# 启动前端
Start-Process -NoNewWindow -FilePath "npm" -ArgumentList "run", "dev" -WorkingDirectory "frontend-next"

Write-Host "开发服务已启动:"
Write-Host "  - Auth:     http://localhost:8001"
Write-Host "  - Chat:     http://localhost:8002"
Write-Host "  - RAG:      http://localhost:8004"
Write-Host "  - Present:  http://localhost:8005"
Write-Host "  - Frontend: http://localhost:3000"
```

#### 6.7.3 方式三：使用 Docker Compose

```bash
# 启动所有服务
docker-compose up -d --build

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 6.8 验证安装

#### 6.8.1 检查后端服务

```bash
# 检查各服务健康状态
curl http://localhost:8001/health  # Auth Service
curl http://localhost:8002/health  # Chat Service
curl http://localhost:8004/health  # RAG Service
curl http://localhost:8005/health  # Presentation Service

# 或使用浏览器访问
# http://localhost:8001/docs  # Auth API 文档
# http://localhost:8002/docs  # Chat API 文档
# http://localhost:8004/docs  # RAG API 文档
# http://localhost:8005/docs  # Presentation API 文档
```

#### 6.8.2 检查前端服务

```bash
# 前端应该自动在浏览器中打开
# 或手动访问: http://localhost:3000
```

### 6.9 常见问题排查

#### 6.9.1 端口被占用

```bash
# Windows: 查找占用端口的进程
netstat -ano | findstr ":8001"

# 杀掉进程
taskkill /PID <进程ID> /F

# 或修改服务端口
uvicorn app.main:app --port 8001 --reload
```

#### 6.9.2 Python 依赖冲突

```bash
# 重新创建环境
conda deactivate
conda remove -n My-Chat-LangChain --all
conda create -n My-Chat-LangChain python=3.10 -y
conda activate My-Chat-LangChain

# 清理缓存后重新安装
pip install --no-cache-dir -r requirements.txt
```

#### 6.9.3 前端构建失败

```bash
# 清理缓存
cd frontend-next
rm -rf .next
rm -rf node_modules
npm install
npm run dev
```

#### 6.9.4 API 连接失败

```bash
# 1. 确认后端服务正在运行
curl http://localhost:8001/health

# 2. 检查 CORS 配置
# 确保后端 .env 中 CORS_ORIGINS 包含前端地址

# 3. 检查防火墙设置
# Windows: 允许 Python 通过防火墙

# 4. 检查代理设置
# 如果使用 Clash Verge 等，可能需要关闭系统代理或添加例外
```

### 6.10 测试配置

#### 6.10.1 安装测试依赖

```bash
# 激活环境
conda activate My-Chat-LangChain

# 安装测试依赖
pip install pytest pytest-asyncio pytest-cov httpx
```

#### 6.10.2 运行测试

```bash
# 运行所有测试
cd backend/auth-service && pytest tests/ -v
cd backend/chat-service && pytest tests/ -v
cd backend/rag-service && pytest tests/ -v
cd backend/presentation-service && pytest tests/ -v

# 运行单个测试文件
pytest tests/test_auth.py -v

# 运行单个测试函数
pytest tests/test_auth.py::test_register -v

# 生成覆盖率报告
pytest tests/ --cov=app --cov-report=html
```

### 6.11 开发工作流

#### 6.11.1 典型开发流程

```
1. 拉取最新代码
   git pull origin master

2. 激活环境
   conda activate My-Chat-LangChain

3. 创建功能分支
   git checkout -b feature/your-feature-name

4. 启动开发服务
   # 使用启动脚本或手动启动

5. 编写代码
   # VS Code 编辑代码

6. 运行测试
   pytest tests/ -v

7. 提交代码
   git add .
   git commit -m "feat: description"

8. 推送到远程
   git push origin feature/your-feature-name
```

#### 6.11.2 代码热重载

- **后端**: 使用 `--reload` 参数，保存代码后自动重启
- **前端**: Next.js 自动热重载，保存后立即在浏览器中看到变化

#### 6.11.3 调试配置

**Python 调试 (VS Code)**:

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Current File",
      "type": "debugpy",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal",
      "justMyCode": true
    },
    {
      "name": "Auth Service",
      "type": "debugpy",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app", "--port", "8001", "--reload"],
      "cwd": "${workspaceFolder}/backend/auth-service",
      "console": "integratedTerminal"
    }
  ]
}
```

---

## 七、部署指南

### 7.1 部署方案总览

My-Chat-LangChain V9.0 支持多种部署方式，从本地开发到云端生产环境：

| 部署方式 | 适用场景 | 成本 | 难度 |
|---------|---------|------|------|
| **本地开发** | 开发测试 | 免费 | 简单 |
| **Docker Compose** | 本地演示、小型团队 | 免费 | 中等 |
| **Render + Supabase** | 生产环境、SaaS 产品 | ~$89/月 | 中等 |
| **自建 VPS** | 完全控制 | $5-20/月 | 复杂 |

### 7.2 云端部署架构 (Render + Supabase)

#### 7.2.1 架构设计图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Render + Supabase 云部署架构                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         Render (计算层)                               │   │
│  │  ┌───────────────────────────────────────────────────────────────┐  │   │
│  │  │  Web Services (5个独立服务)                                    │  │   │
│  │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │  │   │
│  │  │  │ frontend     │  │ auth         │  │ chat         │         │  │   │
│  │  │  │ (Static)     │  │ service      │  │ service      │         │  │   │
│  │  │  │ Port: 3000   │  │ Port: 8001   │  │ Port: 8002   │         │  │   │
│  │  │  │ Starter: $7  │  │ Starter: $7  │  │ Standard:$25 │         │  │   │
│  │  │  └──────────────┘  └──────────────┘  └──────────────┘         │  │   │
│  │  │  ┌──────────────┐  ┌──────────────┐                         │  │   │
│  │  │  │ rag          │  │ present.     │                         │  │   │
│  │  │  │ service      │  │ service      │                         │  │   │
│  │  │  │ Port: 8004   │  │ Port: 8005   │                         │  │   │
│  │  │  │ Standard:$25 │  │ Standard:$25 │                         │  │   │
│  │  │  └──────────────┘  └──────────────┘                         │  │   │
│  │  │  ┌──────────────┐                                             │  │   │
│  │  │  │ whisper      │ (可选)                                   │  │   │
│  │  │  │ service      │                                             │  │   │
│  │  │  │ Port: 8003   │                                             │  │   │
│  │  │  │ Starter: $7  │                                             │  │   │
│  │  │  └──────────────┘                                             │  │   │
│  │  └───────────────────────────────────────────────────────────────┘  │   │
│  │                          │                                         │   │
│  └──────────────────────────┼─────────────────────────────────────────┘   │
│                             │                                             │
│                             ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Supabase (数据层)                               │   │
│  │  ┌───────────────────────────────────────────────────────────────┐  │   │
│  │  │  PostgreSQL Database                                            │  │   │
│  │  │  - pgvector Extension (向量搜索)                                │  │   │
│  │  │  - Tables: users, sessions, messages, documents, chunks      │  │   │
│  │  │  - Row Level Security (用户隔离)                                │  │   │
│  │  │  - Connection Pooling (高并发支持)                              │  │   │
│  │  └───────────────────────────────────────────────────────────────┘  │   │
│  │  ┌───────────────────────────────────────────────────────────────┐  │   │
│  │  │  Supabase Storage (可选)                                       │  │   │
│  │  │  - 文件上传/存储                                                │  │   │
│  │  └───────────────────────────────────────────────────────────────┘  │   │
│  │  ┌───────────────────────────────────────────────────────────────┐  │   │
│  │  │  Supabase Auth (可选，如需替换自建 Auth)                       │  │   │
│  │  │  - 社交登录集成                                                │  │   │
│  │  └───────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  用户访问: https://<app-name>.onrender.com                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 7.2.2 Render 服务配置清单

| 服务 | Root Directory | Build Command | Start Command | 实例类型 |
|------|----------------|---------------|---------------|----------|
| **frontend** | `frontend-next` | `npm install && npm run build` | `npm start` | Free/Starter |
| **auth-service** | `backend/auth-service` | `pip install -r requirements.txt` | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` | Starter |
| **chat-service** | `backend/chat-service` | 同上 | 同上 | Standard |
| **rag-service** | `backend/rag-service` | 同上 | 同上 | Standard |
| **presentation-service** | `backend/presentation-service` | 同上 | 同上 | Standard |
| **whisper-service** | `backend/whisper-service` | 同上 | 同上 | Starter (可选) |

### 7.3 Supabase 数据库配置

#### 7.3.1 创建 Supabase 项目

**步骤 1: 注册并创建项目**

1. 访问 [Supabase](https://supabase.com)
2. 点击 "New Project"
3. 配置项目:
   - **项目名称**: stream-agent-db (或自定义)
   - **数据库密码**: 生成强密码并保存
   - **区域**: 选择离用户最近的区域
     - 推荐: Southeast Asia (Singapore) - 亚洲用户
     - 或: East US (North Virginia) - 美洲用户
4. 点击 "Create new project" 并等待初始化完成 (约 2 分钟)

**步骤 2: 启用 pgvector 扩展**

1. 进入项目 Dashboard
2. 左侧菜单选择 **Database** → **Extensions**
3. 搜索 `pgvector`
4. 点击 **Enable** 启用扩展

**步骤 3: 执行数据库 Schema**

1. 左侧菜单选择 **SQL Editor**
2. 点击 **New Query**
3. 复制 `database/supabase_schema.sql` 全部内容
4. 粘贴到编辑器
5. 点击 **Run** 执行脚本

**Schema 包含**:
- `users` - 用户表
- `refresh_tokens` - Token 刷新表
- `user_settings` - 用户设置
- `api_keys` - API Key 存储
- `conversations` - 会话表
- `messages` - 消息表
- `documents` - 文档表
- `document_chunks` - 文档分块 (含向量)
- 向量搜索函数: `search_documents()`, `hybrid_search()`
- 自动更新时间戳触发器

**步骤 4: 获取数据库连接信息**

1. Settings → **Database**
2. 复制以下连接信息:
   - **Connection string** (URI 格式)
   - **Project URL** (用于 Supabase 客户端)
   - **anon key** (公开密钥)
   - **service_role key** (管理密钥)

**连接字符串格式**:
```
postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
```

**示例**:
```
postgresql://postgres.abc123:mysecretpassword@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
```

> **注意**: 使用 Pooler 连接 (端口 6543) 可以获得更好的连接池性能。

### 7.4 Render 部署步骤

#### 7.4.1 准备工作

**1. 推送代码到 GitHub**

```bash
# 如果还没有 Git 仓库
git init
git add .
git commit -m "Initial commit for Render deployment"

# 创建 GitHub 仓库后
git remote add origin https://github.com/your-username/My-Chat-LangChain.git
git branch -M main
git push -u origin main
```

**2. 注册 Render 账号**

1. 访问 [Render](https://render.com)
2. 使用 GitHub 账号登录 (授权)
3. 验证邮箱

#### 7.4.2 创建数据库服务 (可选)

如果使用 Supabase 作为数据库，可以跳过此步骤。

#### 7.4.3 部署后端服务

**部署 auth-service**

1. Render Dashboard → **New** → **Web Service**
2. 连接 GitHub 仓库
3. 配置服务:
   - **Name**: `stream-agent-auth`
   - **Region**: Oregon (us-west) 或 Singapore
   - **Branch**: `main`
   - **Root Directory**: `backend/auth-service`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. 配置环境变量:
   ```bash
   DATABASE_URL=postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
   JWT_SECRET=your-super-secret-key-at-least-32-characters-long
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   REFRESH_TOKEN_EXPIRE_DAYS=7
   CORS_ORIGINS=["https://stream-agent-frontend.onrender.com"]
   ```

5. 点击 **Create Web Service**

**部署 chat-service**

1. **New** → **Web Service**
2. 配置:
   - **Name**: `stream-agent-chat`
   - **Root Directory**: `backend/chat-service`
   - **Instance Type**: Standard (推荐 2 GB RAM)

3. 环境变量:
   ```bash
   DATABASE_URL=<同 auth-service>
   JWT_SECRET=<同 auth-service>
   AUTH_SERVICE_URL=https://stream-agent-auth.onrender.com
   RAG_SERVICE_URL=https://stream-agent-rag.onrender.com
   PRESENTATION_SERVICE_URL=https://stream-agent-presentation.onrender.com

   # LLM 配置 (二选一)
   GOOGLE_API_KEY=your-google-api-key
   GOOGLE_MODEL=gemini-2.0-flash-exp

   # 或使用 OpenAI
   OPENAI_BASE_URL=https://api.openai.com/v1
   OPENAI_API_KEY=your-openai-api-key
   OPENAI_MODEL=gpt-4o-mini

   # 外部服务
   E2B_API_KEY=your-e2b-api-key
   BRIGHT_DATA_API_KEY=your-bright-data-api-key
   ```

**部署 rag-service**

1. **New** → **Web Service**
2. 配置:
   - **Name**: `stream-agent-rag`
   - **Root Directory**: `backend/rag-service`
   - **Instance Type**: Standard (推荐 2 GB RAM)

3. 环境变量:
   ```bash
   DATABASE_URL=<同 auth-service>
   JWT_SECRET=<同 auth-service>

   # 向量存储
   VECTOR_STORE_BACKEND=pgvector
   PGVECTOR_ENABLED=true
   MILVUS_ENABLED=false

   # Embedding
   EMBEDDING_MODEL=all-MiniLM-L6-v2
   EMBEDDING_DIMENSION=384

   # 搜索配置
   DEFAULT_TOP_K=10
   DEFAULT_ALPHA=0.5
   ENABLE_RERANK=false
   ```

**部署 presentation-service**

1. **New** → **Web Service**
2. 配置:
   - **Name**: `stream-agent-presentation`
   - **Root Directory**: `backend/presentation-service`
   - **Instance Type**: Standard

3. 环境变量:
   ```bash
   DATABASE_URL=<同 auth-service>
   JWT_SECRET=<同 auth-service>
   AUTH_SERVICE_URL=https://stream-agent-auth.onrender.com

   # LLM 配置
   GOOGLE_API_KEY=<同 chat-service>

   # 图片服务
   UNSPLASH_SOURCE_URL=https://source.unsplash.com/featured
   ```

**部署 whisper-service (可选)**

1. **New** → **Web Service**
2. 配置:
   - **Name**: `stream-agent-whisper`
   - **Root Directory**: `backend/whisper-service`
   - **Instance Type**: Starter

3. 环境变量:
   ```bash
   DATABASE_URL=<同 auth-service>
   JWT_SECRET=<同 auth-service>
   ```

#### 7.4.4 部署前端服务

**部署 frontend-next**

1. **New** → **Static Site** (或 Web Service)
2. 配置:
   - **Name**: `stream-agent-frontend`
   - **Root Directory**: `frontend-next`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `.next` (Standalone 模式)

3. 环境变量:
   ```bash
   # API 地址 - 使用 Render 内部网络
   NEXT_PUBLIC_API_URL=https://stream-agent-chat.onrender.com
   NEXT_PUBLIC_AUTH_URL=https://stream-agent-auth.onrender.com
   NEXT_PUBLIC_RAG_URL=https://stream-agent-rag.onrender.com
   NEXT_PUBLIC_PRESENTATION_URL=https://stream-agent-presentation.onrender.com
   NEXT_PUBLIC_WHISPER_URL=https://stream-agent-whisper.onrender.com
   ```

4. 点击 **Create Site**

> **注意**: 首次部署可能需要 5-10 分钟构建时间。

### 7.5 域名配置

#### 7.5.1 配置自定义域名

**在 Render 中配置**

1. 进入服务设置 → **Domains**
2. 点击 **Add Domain**
3. 输入域名: `app.yourdomain.com`
4. 根据提示配置 DNS:

**DNS 配置**:

| 类型 | 名称 | 值 |
|------|------|-----|
| CNAME | `app` | `cname.render.com` |

**使用根域名**:

| 类型 | 名称 | 值 |
|------|------|-----|
| A | `@` | `216.24.57.11` (Render IP) |
| CNAME | `www` | `cname.render.com` |

5. 等待 SSL 证书自动生成 (Let's Encrypt)

#### 7.5.2 健康检查端点

每个服务都提供健康检查端点:

```bash
# 检查所有服务
curl https://stream-agent-auth.onrender.com/health
curl https://stream-agent-chat.onrender.com/health
curl https://stream-agent-rag.onrender.com/health
curl https://stream-agent-presentation.onrender.com/health
curl https://stream-agent-whisper.onrender.com/health
```

**预期响应**:
```json
{
  "status": "healthy",
  "service": "auth-service",
  "version": "1.0.0"
}
```

### 7.6 环境变量完整清单

#### 7.6.1 Auth Service 环境变量

| 变量名 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| `DATABASE_URL` | 是 | - | PostgreSQL 连接字符串 |
| `JWT_SECRET` | 是 | - | JWT 签名密钥 (≥32 字符) |
| `JWT_ALGORITHM` | 否 | `HS256` | JWT 算法 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 否 | `60` | Access Token 有效期 |
| `REFRESH_TOKEN_EXPIRE_DAYS` | 否 | `7` | Refresh Token 有效期 |
| `CORS_ORIGINS` | 否 | `["*"]` | CORS 允许来源 |

#### 7.6.2 Chat Service 环境变量

| 变量名 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| `DATABASE_URL` | 是 | - | PostgreSQL 连接字符串 |
| `JWT_SECRET` | 是 | - | 与 auth-service 相同 |
| `AUTH_SERVICE_URL` | 是 | - | Auth 服务地址 |
| `RAG_SERVICE_URL` | 否 | - | RAG 服务地址 |
| `PRESENTATION_SERVICE_URL` | 否 | - | Presentation 服务地址 |
| `GOOGLE_API_KEY` | 是* | - | Gemini API Key |
| `GOOGLE_MODEL` | 否 | `gemini-2.0-flash-exp` | Gemini 模型 |
| `OPENAI_BASE_URL` | 是* | - | OpenAI API 地址 |
| `OPENAI_API_KEY` | 是* | - | OpenAI API Key |
| `OPENAI_MODEL` | 否 | `gpt-4o-mini` | OpenAI 模型 |
| `E2B_API_KEY` | 否 | - | E2B 代码执行 |
| `BRIGHT_DATA_API_KEY` | 否 | - | MCP 工具 |

\* 至少配置一个 LLM 提供商

#### 7.6.3 RAG Service 环境变量

| 变量名 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| `DATABASE_URL` | 是 | - | PostgreSQL 连接字符串 |
| `JWT_SECRET` | 是 | - | 与 auth-service 相同 |
| `JWT_ENABLED` | 否 | `true` | 启用 JWT 验证 |
| `VECTOR_STORE_BACKEND` | 否 | `pgvector` | 向量存储后端 |
| `PGVECTOR_ENABLED` | 否 | `true` | 启用 pgvector |
| `MILVUS_ENABLED` | 否 | `false` | 启用 Milvus |
| `EMBEDDING_MODEL` | 否 | `all-MiniLM-L6-v2` | Embedding 模型 |
| `EMBEDDING_DIMENSION` | 否 | `384` | 向量维度 |
| `DEFAULT_TOP_K` | 否 | `10` | 检索结果数量 |
| `DEFAULT_ALPHA` | 否 | `0.5` | 混合检索权重 |
| `ENABLE_RERANK` | 否 | `false` | 启用重排序 |

#### 7.6.4 Presentation Service 环境变量

| 变量名 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| `DATABASE_URL` | 是 | - | PostgreSQL 连接字符串 |
| `JWT_SECRET` | 是 | - | 与 auth-service 相同 |
| `AUTH_SERVICE_URL` | 是 | - | Auth 服务地址 |
| `GOOGLE_API_KEY` | 是* | - | Gemini API Key |
| `OPENAI_API_KEY` | 是* | - | OpenAI API Key |
| `E2B_API_KEY` | 否 | - | E2B 代码执行 |
| `UNSPLASH_SOURCE_URL` | 否 | - | Unsplash 图片源 |

#### 7.6.5 Frontend 环境变量

| 变量名 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| `NEXT_PUBLIC_API_URL` | 是 | - | Chat 服务地址 |
| `NEXT_PUBLIC_AUTH_URL` | 是 | - | Auth 服务地址 |
| `NEXT_PUBLIC_RAG_URL` | 是 | - | RAG 服务地址 |
| `NEXT_PUBLIC_PRESENTATION_URL` | 是 | - | Presentation 服务地址 |
| `NEXT_PUBLIC_WHISPER_URL` | 否 | - | Whisper 服务地址 |

### 7.7 成本估算

#### 7.7.1 Render 服务成本

| 服务 | 实例类型 | CPU | RAM | 月费 |
|------|----------|-----|-----|------|
| frontend | Free/Starter | 0.1-0.5 | 512MB | $0-7 |
| auth-service | Starter | 0.5 | 512MB | $7 |
| chat-service | Standard | 1-2 | 2GB | $25 |
| rag-service | Standard | 1-2 | 2GB | $25 |
| presentation-service | Standard | 1-2 | 2GB | $25 |
| whisper-service | Starter | 0.5 | 512MB | $7 |
| **总计** | | | | **$89-96/月** |

#### 7.7.2 Supabase 成本

| 计划 | 存储 | 数据传输 | 月费 |
|------|------|----------|------|
| Free | 500MB | 1GB | $0 |
| Pro | 8GB | 50GB | $25 |
| Team | 100GB | 500GB | $199 |

**推荐**: Free 计划用于测试/小型项目，Pro 计划用于生产环境。

#### 7.7.3 月度总成本

| 场景 | Render | Supabase | 总计 |
|------|--------|----------|------|
| 测试环境 | $7 (最低配置) | $0 | $7/月 |
| 小型生产 | $89 | $0-25 | $89-114/月 |
| 大型生产 | $120+ | $25+ | $145+/月 |

### 7.8 Docker 部署方案

#### 7.8.1 Dockerfile 配置

**前端 Dockerfile** (`frontend-next/Dockerfile`):

```dockerfile
# 多阶段构建 - 优化镜像大小

# Stage 1: 依赖安装
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci --only=production=false

# Stage 2: 构建
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# 构建时环境变量
ARG NEXT_PUBLIC_API_URL=http://localhost:8002
ARG NEXT_PUBLIC_AUTH_URL=http://localhost:8001
ARG NEXT_PUBLIC_RAG_URL=http://localhost:8004
ARG NEXT_PUBLIC_WHISPER_URL=http://localhost:8003

ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_AUTH_URL=$NEXT_PUBLIC_AUTH_URL
ENV NEXT_PUBLIC_RAG_URL=$NEXT_PUBLIC_RAG_URL
ENV NEXT_PUBLIC_WHISPER_URL=$NEXT_PUBLIC_WHISPER_URL
ENV NEXT_TELEMETRY_DISABLED=1

RUN npm run build

# Stage 3: 运行
FROM node:20-alpine AS runner
WORKDIR /app

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

COPY --from=builder /app/public ./public
RUN mkdir .next
RUN chown nextjs:nodejs .next

COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
CMD ["node", "server.js"]
```

**后端 Dockerfile** (`backend/*/Dockerfile`):

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY ./app ./app

# 暴露端口
EXPOSE 8001

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

#### 7.8.2 Docker Compose 编排

创建 `docker-compose.yml`:

```yaml
version: '3.8'

services:
  # PostgreSQL 数据库 (开发环境)
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_USER: streamagent
      POSTGRES_PASSWORD: streamagent_pass
      POSTGRES_DB: streamagent
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U streamagent"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Auth Service
  auth-service:
    build:
      context: ./backend/auth-service
      dockerfile: Dockerfile
    ports:
      - "8001:8001"
    environment:
      DATABASE_URL: postgresql://streamagent:streamagent_pass@postgres:5432/streamagent
      JWT_SECRET: your-super-secret-key-at-least-32-characters-long
    depends_on:
      postgres:
        condition: service_healthy
    restart: unless-stopped

  # Chat Service
  chat-service:
    build:
      context: ./backend/chat-service
      dockerfile: Dockerfile
    ports:
      - "8002:8002"
    environment:
      DATABASE_URL: postgresql://streamagent:streamagent_pass@postgres:5432/streamagent
      JWT_SECRET: your-super-secret-key-at-least-32-characters-long
      AUTH_SERVICE_URL: http://auth-service:8001
      RAG_SERVICE_URL: http://rag-service:8004
      PRESENTATION_SERVICE_URL: http://presentation-service:8005
      GOOGLE_API_KEY: ${GOOGLE_API_KEY}
    depends_on:
      - postgres
      - auth-service
    restart: unless-stopped

  # RAG Service
  rag-service:
    build:
      context: ./backend/rag-service
      dockerfile: Dockerfile
    ports:
      - "8004:8004"
    environment:
      DATABASE_URL: postgresql://streamagent:streamagent_pass@postgres:5432/streamagent
      JWT_SECRET: your-super-secret-key-at-least-32-characters-long
      VECTOR_STORE_BACKEND: pgvector
      PGVECTOR_ENABLED: true
    depends_on:
      - postgres
    restart: unless-stopped

  # Presentation Service
  presentation-service:
    build:
      context: ./backend/presentation-service
      dockerfile: Dockerfile
    ports:
      - "8005:8005"
    environment:
      DATABASE_URL: postgresql://streamagent:streamagent_pass@postgres:5432/streamagent
      JWT_SECRET: your-super-secret-key-at-least-32-characters-long
      AUTH_SERVICE_URL: http://auth-service:8001
      GOOGLE_API_KEY: ${GOOGLE_API_KEY}
    depends_on:
      - postgres
      - auth-service
    restart: unless-stopped

  # Frontend
  frontend:
    build:
      context: ./frontend-next
      dockerfile: Dockerfile
      args:
        NEXT_PUBLIC_API_URL: http://chat-service:8002
        NEXT_PUBLIC_AUTH_URL: http://auth-service:8001
        NEXT_PUBLIC_RAG_URL: http://rag-service:8004
        NEXT_PUBLIC_PRESENTATION_URL: http://presentation-service:8005
    ports:
      - "3000:3000"
    depends_on:
      - auth-service
      - chat-service
      - rag-service
      - presentation-service
    restart: unless-stopped

volumes:
  postgres_data:
```

**启动命令**:

```bash
# 启动所有服务
docker-compose up -d --build

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 停止并删除数据
docker-compose down -v
```

### 7.9 CI/CD 自动化部署

#### 7.9.1 GitHub Actions 配置

创建 `.github/workflows/deploy-render.yml`:

```yaml
name: Deploy to Render

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [auth-service, chat-service, rag-service, presentation-service]

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Deploy to Render
        uses: johnbeynon/render-deploy-action@v0.0.8
        with:
          service-id: ${{ secrets.RENDER_SERVICE_ID }}
          api-key: ${{ secrets.RENDER_API_KEY }}
          wait-for-success: true

  deploy-frontend:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install dependencies
        run: |
          cd frontend-next
          npm ci

      - name: Build
        run: |
          cd frontend-next
          npm run build

      - name: Deploy to Render
        uses: johnbeynon/render-deploy-action@v0.0.8
        with:
          service-id: ${{ secrets.RENDER_FRONTEND_SERVICE_ID }}
          api-key: ${{ secrets.RENDER_API_KEY }}
          wait-for-success: true
```

**配置 GitHub Secrets**:

1. 仓库 Settings → **Secrets and variables** → **Actions**
2. 添加以下 Secrets:
   - `RENDER_API_KEY`: Render API Key (从 Account Settings 获取)
   - `RENDER_SERVICE_ID`: 各服务的 Service ID
   - `RENDER_FRONTEND_SERVICE_ID`: 前端服务的 Service ID

### 7.10 监控与日志

#### 7.10.1 Render 监控

**实时日志**:

```bash
# 使用 Render CLI
npm install -g render-cli
render logs -f stream-agent-chat

# 或在 Dashboard 中查看
# Dashboard → Services → chat-service → Logs
```

**健康检查**:

```bash
# 添加到 cron job
*/5 * * * * curl https://stream-agent-chat.onrender.com/health
```

**自动部署**:

Render 默认监听 GitHub push 事件，自动重新部署：
- 免费计划: 推送后 15 分钟内部署
- 付费计划: 推送后立即部署

#### 7.10.2 Supabase 监控

**数据库监控**:

1. Dashboard → **Database** → **Metrics**
2. 查看:
   - Connection count
   - Storage usage
   - Query performance

**备份**:

- 自动备份: Pro 计划每天自动备份
- 手动备份: Dashboard → Database → Backups

### 7.11 常见问题排查

#### 7.11.1 服务启动失败

**症状**: Render 服务显示 "Deploy failed"

**排查步骤**:

1. **查看部署日志**
   ```
   Dashboard → Services → 服务名 → Logs
   ```

2. **常见原因**:
   - 依赖安装失败 → 检查 `requirements.txt`
   - 环境变量缺失 → 确认所有必需变量已设置
   - 数据库连接超时 → 使用 Supabase Pooler 连接

3. **解决方案**:
   ```bash
   # 本地测试构建
   docker build -t test-build ./backend/auth-service
   docker run test-build
   ```

#### 7.11.2 数据库连接超时

**症状**: `psycopg2.OperationalError: connection timeout`

**解决方案**:

1. **使用 Supabase Pooler** (端口 6543):
   ```bash
   # 标准连接 (可能超时)
   postgresql://...@aws-0-xxx.pooler.supabase.com:5432/postgres

   # Pooler 连接 (推荐)
   postgresql://...@aws-0-xxx.pooler.supabase.com:6543/postgres
   ```

2. **增加连接池大小**:
   - Supabase Dashboard → Database → Connection Pooling
   - Mode: Transaction Mode
   - Pool Size: 增加到 15-20

#### 7.11.3 向量搜索失败

**症状**: `relation "document_chunks" does not exist`

**解决方案**:

1. 确认 Schema 已执行:
   ```sql
   -- 在 Supabase SQL Editor 中执行
   SELECT COUNT(*) FROM document_chunks;
   ```

2. 确认 pgvector 已启用:
   ```sql
   SELECT extname FROM pg_extension WHERE extname = 'vector';
   ```

3. 重新执行 Schema:
   - 复制 `database/supabase_schema.sql`
   - 在 SQL Editor 中运行

#### 7.11.4 前端无法连接后端

**症状**: 浏览器控制台显示 `CORS error` 或 `Network Error`

**解决方案**:

1. **检查 CORS 配置**:
   ```python
   # backend/*/app/main.py
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://stream-agent-frontend.onrender.com"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **检查前端环境变量**:
   ```bash
   # Render Dashboard → frontend → Environment
   NEXT_PUBLIC_API_URL=https://stream-agent-chat.onrender.com
   ```

3. **验证服务可访问**:
   ```bash
   curl https://stream-agent-chat.onrender.com/health
   ```

### 7.12 性能优化建议

#### 7.12.1 数据库优化

**连接池配置**:
```python
# backend/*/app/database.py
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

# Supabase 推荐配置
engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=False
)
```

**索引优化**:
```sql
-- 添加到 Schema
CREATE INDEX CONCURRENTLY idx_messages_created_at_desc
ON messages(created_at DESC);

CREATE INDEX CONCURRENTLY idx_chunks_user_embedding
ON document_chunks(user_id)
INCLUDE (embedding);
```

#### 7.12.2 应用优化

**启用缓存** (可选):

添加 Redis 缓存服务:
```yaml
# docker-compose.yml
redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"
```

**CDN 配置**:

Render 自动提供 CDN:
- 静态资源自动缓存
- 使用 Cloudflare CDN (可选)

#### 7.12.3 成本优化

**降级策略**:

| 服务 | 标准配置 | 降级配置 | 节省 |
|------|----------|----------|------|
| chat-service | Standard ($25) | Starter ($7) | $18/月 |
| rag-service | Standard ($25) | Starter ($7) | $18/月 |
| presentation-service | Standard ($25) | Starter ($7) | $18/月 |

**适用场景**:
- 测试/演示环境
- 低流量应用 (<100 用户/天)

---

*(第七部分完成 - 部署指南)*


## 八、代码阅读指南

本章为开发者提供系统化的代码阅读路径，帮助快速理解项目架构和核心逻辑。

### 8.1 推荐阅读顺序

#### 8.1.1 入门级路径（1-2 小时）

适合初次接触项目的开发者，快速了解整体架构：

```
1. CLAUDE.md                           # 项目概述和开发规范
2. backend/chat-service/app/main.py    # 主服务入口
3. backend/chat-service/app/services/agent_service.py  # Agent 核心
4. frontend-next/src/app/(main)/chat/page.tsx          # 前端聊天页面
```

#### 8.1.2 后端深入路径（3-4 小时）

适合后端开发者深入理解服务架构：

```
阶段 1: 认证服务
├── backend/auth-service/app/main.py           # 服务入口
├── backend/auth-service/app/api/v1/auth.py    # 认证 API
├── backend/auth-service/app/core/security.py  # JWT 实现
└── backend/auth-service/app/models/user.py    # 用户模型

阶段 2: 聊天服务（核心）
├── backend/chat-service/app/main.py           # 服务入口
├── backend/chat-service/app/services/agent_service.py  # Agent 核心
├── backend/chat-service/app/api/v1/chat.py    # 聊天 API
└── backend/tools/                             # 工具集合
    ├── rag_search_tool.py                     # RAG 工具
    └── e2b_tools.py                           # E2B 代码执行

阶段 3: RAG 服务
├── backend/rag-service/app/main.py            # 服务入口
├── backend/rag-service/app/services/search_service.py   # 混合检索
├── backend/rag-service/app/services/pgvector_service.py # 向量存储
├── backend/rag-service/app/services/bm25_service.py     # BM25 检索
└── backend/rag-service/app/services/rerank_service.py   # 重排序

阶段 4: 演示文稿服务
├── backend/presentation-service/app/main.py
├── backend/presentation-service/app/services/presentation_service.py
├── backend/presentation-service/app/services/theme_service.py
└── backend/presentation-service/app/services/layout_engine.py
```

#### 8.1.3 前端深入路径（2-3 小时）

适合前端开发者理解 UI 架构：

```
阶段 1: 应用结构
├── frontend-next/src/app/layout.tsx           # 根布局
├── frontend-next/src/app/(auth)/              # 认证页面组
└── frontend-next/src/app/(main)/              # 主功能页面组

阶段 2: 状态管理
├── frontend-next/src/lib/stores/authStore.ts        # 认证状态
├── frontend-next/src/lib/stores/chatStore.ts        # 聊天状态
├── frontend-next/src/lib/stores/presentationStore.ts # 演示文稿状态
└── frontend-next/src/lib/stores/settingsStore.ts    # 设置状态

阶段 3: 核心组件
├── frontend-next/src/components/chat/
│   ├── ChatContainer.tsx      # 聊天容器
│   ├── MessageList.tsx        # 消息列表
│   ├── MessageBubble.tsx      # 消息气泡
│   ├── InputArea.tsx          # 输入区域
│   ├── ToolCallPanel.tsx      # 工具调用面板
│   └── CitationPanel.tsx      # 引用面板
└── frontend-next/src/components/presentations/
    ├── SlidePreview.tsx       # 幻灯片预览
    └── PresentationPlayer.tsx # 演示播放器
```

### 8.2 核心模块详解

#### 8.2.1 Agent 服务 (agent_service.py)

这是整个系统的核心，负责 AI 对话和工具调用。

**文件位置**: `backend/chat-service/app/services/agent_service.py`

**关键全局变量**:

| 变量 | 类型 | 说明 |
|------|------|------|
| `_agent_executors` | `Dict[str, Any]` | 每用户独立的 Agent 实例 |
| `_mcp_client` | `MultiServerMCPClient` | MCP 工具客户端 |
| `_mcp_tools` | `List` | MCP 工具列表 |
| `_sqlite_conn` | `aiosqlite.Connection` | SQLite 连接（会话持久化） |

**核心函数**:

| 函数 | 职责 |
|------|------|
| `get_tools(api_keys)` | 加载 MCP 工具和自定义工具 |
| `initialize_agent(user_id, api_keys)` | 初始化用户专属的 LangGraph Agent |
| `chat_with_agent_stream(...)` | 流式对话核心函数 |
| `cleanup()` | 清理资源 |

**关键设计模式**:
- **用户隔离**: 每个用户有独立的 Agent 实例，通过 `_agent_executors[user_id]` 管理
- **会话持久化**: 使用 `AsyncSqliteSaver` 保存对话状态，支持多轮对话
- **SSE 流式输出**: Base64 编码避免换行问题
- **RAG 引用追溯**: 解析 `[RAG_CITATIONS]` 标记，提取引用信息

**代码片段 - Agent 初始化**:
```python
async def initialize_agent(user_id: str, api_keys: Dict[str, str] = None) -> Any:
    global _agent_executors, _sqlite_conn

    # 检查是否已存在该用户的 Agent
    if user_id in _agent_executors:
        return _agent_executors[user_id]

    # 加载工具
    all_tools = await get_tools(api_keys)

    # 配置 LLM (Gemini 或 OpenAI 兼容)
    if llm_provider == "openai_compatible":
        llm = ChatOpenAI(...)
    else:
        llm = ChatGoogleGenerativeAI(...)

    # 创建 SQLite 连接用于会话持久化
    if _sqlite_conn is None:
        _sqlite_conn = await aiosqlite.connect(DB_PATH)
    checkpointer = AsyncSqliteSaver(_sqlite_conn)

    # 创建 ReAct Agent
    agent_executor = create_react_agent(
        model=llm,
        tools=all_tools,
        checkpointer=checkpointer,
    )

    _agent_executors[user_id] = agent_executor
    return agent_executor
```

#### 8.2.2 混合检索服务 (search_service.py)

实现向量 + BM25 混合检索。

**文件位置**: `backend/rag-service/app/services/search_service.py`

**核心类**: `HybridSearchService`

**检索流程**:
```
用户查询
    │
    ├──→ 向量检索 (语义相似度)
    │         │
    │         ▼
    │    VectorSearchResult[]
    │         │
    └──→ BM25 检索 (关键词匹配)
              │
              ▼
         BM25Result[]
              │
              ▼
        RRF 融合算法
              │
              ▼
        FusedResult[]
              │
              ▼
        Reranker 重排序 (可选)
              │
              ▼
        SearchResult[]
```

**RRF 融合算法**:
```python
def rrf_fusion(self, vector_results, bm25_results, alpha=0.5, k=60):
    # 公式: RRF(d) = sum(1 / (k + r_i))
    # alpha: 向量权重, (1-alpha): BM25 权重

    scores: Dict[str, Dict[str, Any]] = {}

    # 处理向量检索结果
    for rank, result in enumerate(vector_results):
        rrf_score = alpha / (k + rank + 1)
        scores[chunk_id]["fused_score"] += rrf_score

    # 处理 BM25 结果
    for rank, result in enumerate(bm25_results):
        rrf_score = (1 - alpha) / (k + rank + 1)
        scores[chunk_id]["fused_score"] += rrf_score

    # 按融合分数排序
    return sorted(scores.items(), key=lambda x: x[1]["fused_score"], reverse=True)
```

#### 8.2.3 演示文稿服务 (presentation_service.py)

AI 驱动的 PPT 生成。

**文件位置**: `backend/presentation-service/app/services/presentation_service.py`

**核心类**: `PresentationService`

**生成流程**:
1. **自动主题推荐** (可选): `theme_service.suggest_theme(topic)`
2. **AI 生成幻灯片内容**: 调用 LLM 生成 JSON 结构
3. **添加图片**: 使用 Picsum 服务获取配图
4. **保存到数据库**: 创建 Presentation 记录

### 8.3 数据流图

#### 8.3.1 聊天请求完整流程

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           用户发送消息                                   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Frontend (chatStore.ts)                                                │
│  sendMessage() → fetch('/api/v1/chat/stream', { SSE })                  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Chat Service (chat.py)                                                 │
│  POST /api/v1/chat/stream                                               │
│  → 验证 JWT Token                                                       │
│  → 调用 chat_with_agent_stream()                                        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Agent Service (agent_service.py)                                       │
│  1. initialize_agent(user_id)                                           │
│  2. 构建消息: [SystemMessage, ...history, HumanMessage]                 │
│  3. agent.astream_events() 流式执行                                     │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
            ┌───────────┐   ┌───────────┐   ┌───────────┐
            │ MCP Tools │   │ RAG Tools │   │ E2B Tools │
            │ (90+)     │   │           │   │           │
            └───────────┘   └───────────┘   └───────────┘
                    │               │               │
                    └───────────────┼───────────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  SSE 事件流                                                             │
│  event: text       → AI 文本输出                                        │
│  event: tool_start → 工具开始执行                                       │
│  event: tool_end   → 工具执行结果                                       │
│  event: citation   → RAG 引用数据                                       │
│  event: done       → 完成标记                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 8.3.2 RAG 检索流程

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         rag_search 工具调用                             │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  RAG Service API                                                        │
│  POST /api/v1/search                                                    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  HybridSearchService.search()                                           │
│  1. EmbeddingService.embed_query(query)  → 查询向量化                   │
│  2. PgvectorService.search()             → 向量检索                     │
│  3. BM25Service.search()                 → 关键词检索                   │
│  4. rrf_fusion()                         → RRF 融合                     │
│  5. RerankService.rerank()               → 重排序 (可选)                │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  返回结果 (带引用信息)                                                  │
│  SearchResult:                                                          │
│    - chunk_id, document_id, document_name                               │
│    - content, page_number                                               │
│    - score, vector_score, bm25_score, rerank_score                      │
└─────────────────────────────────────────────────────────────────────────┘
```

### 8.4 关键设计模式

#### 8.4.1 微服务通信模式

| 通信方式 | 场景 | 示例 |
|----------|------|------|
| HTTP/REST | 前端 ↔ 后端 | `POST /api/v1/chat/stream` |
| HTTP/REST | 服务间同步调用 | Chat → RAG 检索 |
| SSE | 流式响应 | 聊天文本流 |
| 独立数据库 | 数据隔离 | 各服务独立 PostgreSQL/SQLite |

#### 8.4.2 状态管理模式 (Zustand)

```typescript
// frontend-next/src/lib/stores/chatStore.ts
interface ChatState {
  // 状态
  conversations: Conversation[]
  currentConversation: Conversation | null
  messages: Message[]
  isLoading: boolean

  // 动作
  sendMessage: (content: string, images?: string[]) => Promise<void>
  loadConversations: () => Promise<void>
  selectConversation: (id: string) => Promise<void>
}

export const useChatStore = create<ChatState>((set, get) => ({
  // 初始状态
  conversations: [],
  currentConversation: null,
  messages: [],
  isLoading: false,

  // 发送消息 (SSE 流式处理)
  sendMessage: async (content, images) => {
    // 1. 添加用户消息到 UI
    // 2. 创建 EventSource 连接
    // 3. 处理 SSE 事件流
    // 4. 更新 AI 响应
  },
}))
```

#### 8.4.3 LangGraph ReAct Agent 模式

```python
# Agent 创建
agent_executor = create_react_agent(
    model=llm,           # Gemini 或 OpenAI
    tools=all_tools,     # MCP + 自定义工具
    checkpointer=checkpointer,  # 会话持久化
)

# ReAct 循环:
# 1. Reasoning: LLM 分析用户意图
# 2. Action: 选择并执行工具
# 3. Observation: 获取工具结果
# 4. 重复直到完成
```

### 8.5 调试技巧

#### 8.5.1 后端调试

```bash
# 启动服务时启用详细日志
cd backend/chat-service
uvicorn app.main:app --port 8002 --reload --log-level debug

# Agent 日志输出示例:
# "Loaded {n} MCP tools."
# "Using Google Gemini LLM: {model}"
# "Agent initialized for user {user_id}"
```

#### 8.5.2 前端调试

```typescript
// 在 chatStore.ts 中添加调试日志
sendMessage: async (content, images) => {
  console.log('[ChatStore] Sending message:', content)

  // SSE 事件处理
  eventSource.onmessage = (event) => {
    console.log('[SSE] Event:', event.type, event.data)
  }
}
```

#### 8.5.3 常用调试命令

```bash
# 测试后端健康检查
curl http://localhost:8002/health

# 测试 RAG 检索
curl -X POST http://localhost:8004/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "测试查询", "top_k": 5}'

# 查看数据库内容 (SQLite)
sqlite3 backend/chat-service/data/state.db ".tables"
sqlite3 backend/chat-service/data/state.db "SELECT * FROM checkpoints LIMIT 5;"
```

### 8.6 扩展开发指南

#### 8.6.1 添加新工具

**步骤 1**: 在 `backend/tools/` 创建新工具文件

```python
# backend/tools/my_new_tool.py
from langchain_core.tools import tool

@tool
def my_new_tool(param1: str, param2: int) -> str:
    """
    工具描述 (会被 LLM 读取用于决策)

    Args:
        param1: 参数1说明
        param2: 参数2说明

    Returns:
        返回值说明
    """
    # 实现逻辑
    return result
```

**步骤 2**: 在 `agent_service.py` 中导入并注册

```python
from tools.my_new_tool import my_new_tool

custom_tools = [
    # ... 现有工具
    my_new_tool,
]
```

#### 8.6.2 添加新服务

**目录结构**:
```
backend/new-service/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI 入口
│   ├── config.py        # 配置
│   ├── database.py      # 数据库
│   ├── api/v1/          # API 路由
│   ├── models/          # SQLAlchemy 模型
│   ├── schemas/         # Pydantic Schema
│   └── services/        # 业务逻辑
└── tests/               # 测试
```

**main.py 模板**:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="New Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

#### 8.6.3 添加新前端页面

**步骤 1**: 创建页面文件

```typescript
// frontend-next/src/app/(main)/new-feature/page.tsx
'use client'

import { useEffect } from 'react'
import { useNewFeatureStore } from '@/lib/stores/newFeatureStore'

export default function NewFeaturePage() {
  const { data, loadData } = useNewFeatureStore()

  useEffect(() => {
    loadData()
  }, [])

  return (
    <div className="container mx-auto p-4">
      <h1>New Feature</h1>
      {/* 页面内容 */}
    </div>
  )
}
```

**步骤 2**: 创建 Store

```typescript
// frontend-next/src/lib/stores/newFeatureStore.ts
import { create } from 'zustand'

interface NewFeatureState {
  data: any[]
  loadData: () => Promise<void>
}

export const useNewFeatureStore = create<NewFeatureState>((set) => ({
  data: [],
  loadData: async () => {
    const response = await fetch('/api/v1/new-feature')
    const data = await response.json()
    set({ data })
  },
}))
```

---

*(第八部分完成 - 代码阅读指南)*


## 9. API 接口文档

本章详细描述各服务的 RESTful API 接口，包括请求/响应格式、认证方式和错误处理。

### 9.1 API 概览

#### 9.1.1 服务端点

| 服务 | 基础 URL | 说明 |
|------|----------|------|
| Auth Service | `http://localhost:8001` | 用户认证 |
| Chat Service | `http://localhost:8002` | 聊天对话 |
| RAG Service | `http://localhost:8004` | 文档检索 |
| Presentation Service | `http://localhost:8005` | 演示文稿 |

#### 9.1.2 认证方式

所有需要认证的接口使用 **JWT Bearer Token**：

```http
Authorization: Bearer <access_token>
```

Token 获取流程：
1. 调用 `/api/auth/login` 获取 `access_token` 和 `refresh_token`
2. `access_token` 有效期 30 分钟
3. `refresh_token` 有效期 7 天
4. Token 过期后调用 `/api/auth/refresh` 刷新

#### 9.1.3 通用响应格式

**成功响应**:
```json
{
  "data": { ... },
  "message": "Success"
}
```

**错误响应**:
```json
{
  "detail": "Error message"
}
```

**HTTP 状态码**:

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 204 | 删除成功（无内容） |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

### 9.2 Auth Service API (端口 8001)

#### 9.2.1 用户注册

```http
POST /api/auth/register
Content-Type: application/json
```

**请求体**:
```json
{
  "username": "string (3-50字符, 字母数字下划线)",
  "email": "string (有效邮箱)",
  "password": "string (8-100字符, 需包含大小写和数字)"
}
```

**响应** (201 Created):
```json
{
  "id": "uuid",
  "username": "string",
  "email": "string",
  "is_active": true,
  "created_at": "datetime"
}
```

**错误**:
- 400: 用户名或邮箱已存在

#### 9.2.2 用户登录

```http
POST /api/auth/login
Content-Type: application/json
```

**请求体**:
```json
{
  "email": "string",
  "password": "string"
}
```

**响应** (200 OK):
```json
{
  "access_token": "string (JWT)",
  "refresh_token": "string (JWT)",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**错误**:
- 401: 邮箱或密码错误

#### 9.2.3 刷新 Token

```http
POST /api/auth/refresh
Content-Type: application/json
```

**请求体**:
```json
{
  "refresh_token": "string"
}
```

**响应** (200 OK):
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### 9.2.4 获取当前用户

```http
GET /api/auth/me
Authorization: Bearer <access_token>
```

**响应** (200 OK):
```json
{
  "id": "uuid",
  "username": "string",
  "email": "string",
  "is_active": true,
  "created_at": "datetime"
}
```

#### 9.2.5 验证 Token

```http
GET /api/auth/verify
Authorization: Bearer <access_token>
```

**响应** (200 OK):
```json
{
  "user_id": "uuid",
  "id": "uuid",
  "username": "string",
  "email": "string",
  "is_active": true
}
```

**说明**: 此接口供其他服务验证 Token 使用。

#### 9.2.6 用户登出

```http
POST /api/auth/logout
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求体**:
```json
{
  "refresh_token": "string"
}
```

**响应** (204 No Content)

---

### 9.3 Chat Service API (端口 8002)

#### 9.3.1 流式聊天

```http
POST /api/chat/stream
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求体**:
```json
{
  "content": "string (用户消息)",
  "conversation_id": "uuid (可选, 不传则创建新会话)",
  "images": ["base64_string (可选, 图片数组)"],
  "api_keys": {
    "GOOGLE_API_KEY": "string (可选)",
    "BRIGHT_DATA_API_KEY": "string (可选)"
  }
}
```

**响应**: Server-Sent Events (SSE) 流

**SSE 事件类型**:

| 事件 | 数据格式 | 说明 |
|------|----------|------|
| `text` | Base64 编码文本 | AI 文本响应片段 |
| `tool_start` | Base64 编码工具名 | 工具开始执行 |
| `tool_end` | Base64 编码 JSON | 工具执行结果 |
| `citation` | Base64 编码 JSON | RAG 引用数据 |
| `done` | Base64 编码 JSON | 流结束标记 |
| `error` | Base64 编码错误信息 | 错误信息 |

**SSE 示例**:
```
event: text
data: SGVsbG8sIEkgY2FuIGhlbHA=

event: tool_start
data: cmFnX3NlYXJjaA==

event: tool_end
data: eyJuYW1lIjogInJhZ19zZWFyY2giLCAib3V0cHV0IjogIi4uLiJ9

event: citation
data: eyJjaHVua19pZCI6ICIuLi4iLCAiZG9jdW1lbnRfbmFtZSI6ICIuLi4ifQ==

event: done
data: eyJjb252ZXJzYXRpb25faWQiOiAidXVpZCJ9
```

**响应头**:
```http
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
X-Conversation-Id: <conversation_id>
```

#### 9.3.2 停止聊天

```http
POST /api/chat/stop
Authorization: Bearer <access_token>
```

**响应** (200 OK):
```json
{
  "status": "ok",
  "message": "Stream stop requested"
}
```

**说明**: 实际停止由客户端关闭连接实现。

#### 9.3.3 会话管理 API

**获取会话列表**:
```http
GET /api/conversations?skip=0&limit=20
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "conversations": [
    {
      "id": "uuid",
      "title": "string",
      "created_at": "datetime",
      "updated_at": "datetime"
    }
  ],
  "total": 100
}
```

**获取会话详情**:
```http
GET /api/conversations/{conversation_id}
Authorization: Bearer <access_token>
```

**获取会话消息**:
```http
GET /api/conversations/{conversation_id}/messages?skip=0&limit=50
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "messages": [
    {
      "id": "uuid",
      "role": "user | assistant",
      "content": "string",
      "images": ["base64"],
      "tool_calls": [...],
      "citations": [...],
      "created_at": "datetime"
    }
  ],
  "total": 50
}
```

**删除会话**:
```http
DELETE /api/conversations/{conversation_id}
Authorization: Bearer <access_token>
```

**响应** (204 No Content)

---

### 9.4 RAG Service API (端口 8004)

#### 9.4.1 混合检索

```http
POST /api/v1/search
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求体**:
```json
{
  "query": "string (查询文本)",
  "top_k": 10,
  "alpha": 0.5,
  "rerank": true,
  "document_ids": ["uuid (可选, 限定文档范围)"]
}
```

**参数说明**:

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `query` | string | 必填 | 查询文本 |
| `top_k` | int | 10 | 返回结果数量 |
| `alpha` | float | 0.5 | 向量权重 (0-1), 1=纯向量, 0=纯BM25 |
| `rerank` | bool | true | 是否使用 Reranker 重排序 |
| `document_ids` | list | null | 限定检索的文档 ID 列表 |

**响应** (200 OK):
```json
{
  "query": "string",
  "total": 10,
  "results": [
    {
      "chunk_id": "uuid",
      "document_id": "uuid",
      "document_name": "string",
      "content": "string",
      "page_number": 1,
      "score": 0.95,
      "vector_score": 0.92,
      "bm25_score": 0.88,
      "rerank_score": 0.95,
      "metadata": {}
    }
  ],
  "search_time_ms": 150.5,
  "citations": [...]
}
```

#### 9.4.2 仅向量检索

```http
POST /api/v1/search/vector
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求体**: 同混合检索（忽略 `alpha` 和 `rerank`）

#### 9.4.3 仅 BM25 检索

```http
POST /api/v1/search/bm25
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求体**: 同混合检索（忽略 `alpha` 和 `rerank`）

#### 9.4.4 获取引用详情

```http
POST /api/v1/search/citations
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求体**:
```json
{
  "chunk_ids": ["uuid"],
  "include_context": true,
  "context_size": 1
}
```

**响应**:
```json
[
  {
    "chunk_id": "uuid",
    "document_id": "uuid",
    "document_name": "string",
    "content": "string",
    "page_number": 1,
    "context_before": ["前文内容"],
    "context_after": ["后文内容"]
  }
]
```

#### 9.4.5 获取单个引用

```http
GET /api/v1/search/citations/{chunk_id}?include_context=true&context_size=1
Authorization: Bearer <access_token>
```

---

### 9.5 Documents API (RAG Service)

#### 9.5.1 获取文档列表

```http
GET /api/v1/documents?skip=0&limit=20
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "total": 50,
  "documents": [
    {
      "id": "uuid",
      "filename": "string",
      "file_type": "pdf | docx | txt",
      "file_size": 1024000,
      "status": "pending | processing | completed | failed",
      "chunk_count": 100,
      "created_at": "datetime",
      "updated_at": "datetime"
    }
  ]
}
```

#### 9.5.2 获取文档详情

```http
GET /api/v1/documents/{document_id}
Authorization: Bearer <access_token>
```

#### 9.5.3 获取文档处理状态

```http
GET /api/v1/documents/{document_id}/status
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "id": "uuid",
  "filename": "string",
  "status": "processing",
  "chunk_count": 50,
  "error_message": null,
  "estimated_time": 30
}
```

#### 9.5.4 删除文档

```http
DELETE /api/v1/documents/{document_id}
Authorization: Bearer <access_token>
```

**响应** (204 No Content)

**说明**: 同时删除 PostgreSQL 记录和向量存储中的数据。

---

### 9.6 Presentation Service API (端口 8005)

#### 9.6.1 获取演示文稿列表

```http
GET /api/v1/presentations?skip=0&limit=20&status_filter=completed
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "presentations": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "title": "string",
      "description": "string",
      "slides": [...],
      "theme": "modern_business",
      "slide_count": 10,
      "status": "draft | completed",
      "created_at": "datetime",
      "updated_at": "datetime"
    }
  ],
  "total": 50,
  "page": 1,
  "page_size": 20
}
```

#### 9.6.2 创建演示文稿

```http
POST /api/v1/presentations
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求体**:
```json
{
  "title": "string",
  "description": "string (可选)",
  "slides": [
    {
      "type": "title | content | two_column | image | quote",
      "title": "string",
      "content": "string | string[]",
      "image_url": "string (可选)",
      "speaker_notes": "string (可选)"
    }
  ],
  "theme": "modern_business",
  "target_audience": "general",
  "presentation_type": "informative",
  "include_images": true,
  "image_style": "professional"
}
```

**响应** (201 Created): 完整的演示文稿对象

#### 9.6.3 AI 生成演示文稿

```http
POST /api/v1/presentations/generate
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求体**:
```json
{
  "topic": "string (主题)",
  "slide_count": 10,
  "target_audience": "general | professional | academic",
  "presentation_type": "informative | persuasive | educational",
  "theme": "modern_business",
  "include_images": true,
  "image_style": "professional | creative | minimal",
  "language": "zh-CN | en-US",
  "custom_title": "string (可选)",
  "auto_theme": false
}
```

**响应** (201 Created): 完整的演示文稿对象

#### 9.6.4 获取演示文稿详情

```http
GET /api/v1/presentations/{presentation_id}
Authorization: Bearer <access_token>
```

#### 9.6.5 更新演示文稿

```http
PUT /api/v1/presentations/{presentation_id}
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求体** (所有字段可选):
```json
{
  "title": "string",
  "description": "string",
  "slides": [...],
  "theme": "string",
  "custom_theme": {},
  "layout_config": {},
  "status": "draft | completed"
}
```

#### 9.6.6 删除演示文稿

```http
DELETE /api/v1/presentations/{presentation_id}
Authorization: Bearer <access_token>
```

**响应** (204 No Content)

#### 9.6.7 导出为 HTML

```http
GET /api/v1/presentations/{presentation_id}/export/html?include_reveal_js=true
Authorization: Bearer <access_token>
```

**响应**: HTML 文件下载

**响应头**:
```http
Content-Type: text/html
Content-Disposition: attachment; filename="presentation.html"; filename*=UTF-8''演示文稿.html
```

#### 9.6.8 预览 HTML

```http
GET /api/v1/presentations/{presentation_id}/export/preview
Authorization: Bearer <access_token>
```

**响应**: HTML 内容（直接在浏览器中渲染）

---

### 9.7 健康检查 API

所有服务都提供健康检查端点：

```http
GET /health
```

**响应**:
```json
{
  "status": "healthy",
  "service": "service-name",
  "version": "1.0.0",
  "database": "connected"
}
```

---

### 9.8 错误处理

#### 9.8.1 通用错误格式

```json
{
  "detail": "Error message describing what went wrong"
}
```

#### 9.8.2 验证错误格式

```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

#### 9.8.3 常见错误码

| 错误码 | 场景 | 解决方案 |
|--------|------|----------|
| 401 Unauthorized | Token 无效或过期 | 刷新 Token 或重新登录 |
| 403 Forbidden | 无权访问资源 | 检查用户权限 |
| 404 Not Found | 资源不存在 | 检查 ID 是否正确 |
| 422 Unprocessable Entity | 请求参数验证失败 | 检查请求体格式 |
| 500 Internal Server Error | 服务器内部错误 | 查看服务日志 |

---

### 9.9 API 调用示例

#### 9.9.1 Python 示例

```python
import requests

BASE_URL = "http://localhost:8001"

# 登录获取 Token
response = requests.post(f"{BASE_URL}/api/auth/login", json={
    "email": "user@example.com",
    "password": "Password123"
})
tokens = response.json()
access_token = tokens["access_token"]

# 使用 Token 调用 API
headers = {"Authorization": f"Bearer {access_token}"}

# 获取用户信息
user = requests.get(f"{BASE_URL}/api/auth/me", headers=headers).json()
print(f"User: {user['username']}")
```

#### 9.9.2 JavaScript/TypeScript 示例

```typescript
const BASE_URL = "http://localhost:8002";

// 流式聊天
async function streamChat(message: string, token: string) {
  const response = await fetch(`${BASE_URL}/api/chat/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
    },
    body: JSON.stringify({ content: message }),
  });

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader!.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split("\n");

    for (const line of lines) {
      if (line.startsWith("event: ")) {
        const eventType = line.slice(7);
        console.log("Event:", eventType);
      } else if (line.startsWith("data: ")) {
        const data = atob(line.slice(6));  // Base64 解码
        console.log("Data:", data);
      }
    }
  }
}
```

#### 9.9.3 cURL 示例

```bash
# 登录
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "Password123"}'

# 使用 Token 调用 API
TOKEN="your_access_token"

# 获取文档列表
curl http://localhost:8004/api/v1/documents \
  -H "Authorization: Bearer $TOKEN"

# 混合检索
curl -X POST http://localhost:8004/api/v1/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "人工智能", "top_k": 5}'
```

---

*(第九部分完成 - API 接口文档)*


## 10. 数据库设计

本章详细描述各服务的数据库表结构、关系和索引设计。

### 10.1 数据库架构概览

#### 10.1.1 数据库分布

| 服务 | 数据库类型 | 用途 |
|------|------------|------|
| Auth Service | PostgreSQL / SQLite | 用户认证数据 |
| Chat Service | PostgreSQL / SQLite | 会话和消息数据 |
| RAG Service | PostgreSQL + pgvector | 文档元数据 + 向量存储 |
| Presentation Service | PostgreSQL / SQLite | 演示文稿数据 |

#### 10.1.2 数据库连接配置

**生产环境** (PostgreSQL + Supabase):
```
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname
```

**开发环境** (SQLite):
```
DATABASE_URL=sqlite+aiosqlite:///./data/app.db
```

---

### 10.2 Auth Service 数据库

#### 10.2.1 users 表

存储用户账户信息。

```sql
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE UNIQUE INDEX ix_users_username ON users(username);
CREATE UNIQUE INDEX ix_users_email ON users(email);
```

**字段说明**:

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | VARCHAR(36) | UUID 主键 |
| `username` | VARCHAR(50) | 用户名，唯一 |
| `email` | VARCHAR(255) | 邮箱，唯一 |
| `password_hash` | VARCHAR(255) | bcrypt 加密的密码哈希 |
| `is_active` | BOOLEAN | 账户是否激活 |
| `is_verified` | BOOLEAN | 邮箱是否验证 |
| `created_at` | TIMESTAMP | 创建时间 |
| `updated_at` | TIMESTAMP | 更新时间 |

#### 10.2.2 refresh_tokens 表

存储刷新令牌，用于 JWT 刷新机制。

```sql
CREATE TABLE refresh_tokens (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_revoked BOOLEAN DEFAULT FALSE
);

-- 索引
CREATE INDEX ix_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE UNIQUE INDEX ix_refresh_tokens_token_hash ON refresh_tokens(token_hash);
```

**字段说明**:

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | VARCHAR(36) | UUID 主键 |
| `user_id` | VARCHAR(36) | 关联用户 ID |
| `token_hash` | VARCHAR(255) | Token 哈希值 |
| `expires_at` | TIMESTAMP | 过期时间 |
| `is_revoked` | BOOLEAN | 是否已撤销 |

---

### 10.3 Chat Service 数据库

#### 10.3.1 conversations 表

存储聊天会话。

```sql
CREATE TABLE conversations (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    title VARCHAR(255) DEFAULT 'New Chat',
    model VARCHAR(50),
    message_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX ix_conversations_user_id ON conversations(user_id);
```

**字段说明**:

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | VARCHAR(36) | UUID 主键 |
| `user_id` | VARCHAR(36) | 用户 ID |
| `title` | VARCHAR(255) | 会话标题 |
| `model` | VARCHAR(50) | 使用的模型名称 |
| `message_count` | INTEGER | 消息数量 |
| `created_at` | TIMESTAMP | 创建时间 |
| `updated_at` | TIMESTAMP | 最后更新时间 |

#### 10.3.2 messages 表

存储聊天消息。

```sql
CREATE TABLE messages (
    id VARCHAR(36) PRIMARY KEY,
    conversation_id VARCHAR(36) NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    images JSON,
    tool_calls JSON,
    citations JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX ix_messages_conversation_id ON messages(conversation_id);
```

**字段说明**:

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | VARCHAR(36) | UUID 主键 |
| `conversation_id` | VARCHAR(36) | 关联会话 ID |
| `role` | VARCHAR(20) | 角色: user / assistant / system |
| `content` | TEXT | 消息内容 |
| `images` | JSON | Base64 图片数组 |
| `tool_calls` | JSON | 工具调用记录 |
| `citations` | JSON | RAG 引用数据 |
| `created_at` | TIMESTAMP | 创建时间 |

**tool_calls JSON 结构**:
```json
[
  {
    "id": "tool_0",
    "name": "rag_search",
    "args": {"query": "..."},
    "status": "success",
    "output": "...",
    "duration": 1.5
  }
]
```

**citations JSON 结构**:
```json
[
  {
    "chunk_id": "uuid",
    "document_id": "uuid",
    "document_name": "文档名.pdf",
    "page_number": 5,
    "content": "引用内容...",
    "score": 0.95
  }
]
```

---

### 10.4 RAG Service 数据库

#### 10.4.1 documents 表

存储文档元数据。

```sql
CREATE TABLE documents (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50),
    file_size INTEGER,
    file_path VARCHAR(500),
    milvus_collection VARCHAR(100),
    chunk_count INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX ix_documents_user_id ON documents(user_id);
CREATE INDEX ix_documents_status ON documents(status);
```

**字段说明**:

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | VARCHAR(36) | UUID 主键 |
| `user_id` | VARCHAR(36) | 用户 ID |
| `filename` | VARCHAR(255) | 原始文件名 |
| `file_type` | VARCHAR(50) | 文件类型 (pdf/docx/txt) |
| `file_size` | INTEGER | 文件大小 (字节) |
| `file_path` | VARCHAR(500) | 存储路径 |
| `milvus_collection` | VARCHAR(100) | Milvus 集合名 |
| `chunk_count` | INTEGER | 分块数量 |
| `status` | VARCHAR(20) | 状态: pending/processing/ready/error |
| `error_message` | TEXT | 错误信息 |

**状态枚举**:
```python
class DocumentStatus(str, Enum):
    PENDING = "pending"      # 等待处理
    PROCESSING = "processing"  # 处理中
    READY = "ready"          # 处理完成
    ERROR = "error"          # 处理失败
```

#### 10.4.2 chunks 表

存储文档分块（用于 BM25 检索）。

```sql
CREATE TABLE chunks (
    id VARCHAR(36) PRIMARY KEY,
    document_id VARCHAR(36) NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    user_id VARCHAR(36) NOT NULL,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    page_number INTEGER,
    extra_data JSON DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX ix_chunks_document_id ON chunks(document_id);
CREATE INDEX ix_chunks_user_id ON chunks(user_id);
```

**字段说明**:

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | VARCHAR(36) | UUID 主键 |
| `document_id` | VARCHAR(36) | 关联文档 ID |
| `user_id` | VARCHAR(36) | 用户 ID |
| `chunk_index` | INTEGER | 分块序号 |
| `content` | TEXT | 分块文本内容 |
| `page_number` | INTEGER | 所在页码 |
| `extra_data` | JSON | 额外元数据 |

#### 10.4.3 pgvector 向量存储

使用 PostgreSQL pgvector 扩展存储向量。

```sql
-- 启用 pgvector 扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 向量表 (由 pgvector_service 管理)
CREATE TABLE IF NOT EXISTS document_vectors (
    id VARCHAR(36) PRIMARY KEY,
    document_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    chunk_id VARCHAR(36) NOT NULL,
    content TEXT NOT NULL,
    page_number INTEGER,
    embedding vector(768),  -- Gemini embedding 维度
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 向量索引 (IVFFlat)
CREATE INDEX IF NOT EXISTS ix_document_vectors_embedding
ON document_vectors USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- 过滤索引
CREATE INDEX IF NOT EXISTS ix_document_vectors_user_id ON document_vectors(user_id);
CREATE INDEX IF NOT EXISTS ix_document_vectors_document_id ON document_vectors(document_id);
```

**向量检索示例**:
```sql
-- 余弦相似度检索
SELECT id, content, page_number,
       1 - (embedding <=> $1::vector) AS similarity
FROM document_vectors
WHERE user_id = $2
ORDER BY embedding <=> $1::vector
LIMIT 10;
```

---

### 10.5 Presentation Service 数据库

#### 10.5.1 presentations 表

存储演示文稿数据。

```sql
CREATE TABLE presentations (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    slides JSON NOT NULL DEFAULT '[]',
    layout_config JSON NOT NULL DEFAULT '{}',
    theme VARCHAR(50) NOT NULL DEFAULT 'modern_business',
    custom_theme JSON,
    target_audience VARCHAR(100),
    presentation_type VARCHAR(50),
    include_images BOOLEAN NOT NULL DEFAULT TRUE,
    image_style VARCHAR(50),
    slide_count INTEGER NOT NULL DEFAULT 0,
    thumbnail TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX ix_presentations_user_id ON presentations(user_id);
CREATE INDEX ix_presentations_status ON presentations(status);
```

**字段说明**:

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | VARCHAR(36) | UUID 主键 |
| `user_id` | VARCHAR(36) | 用户 ID |
| `title` | VARCHAR(255) | 演示文稿标题 |
| `description` | TEXT | 描述 |
| `slides` | JSON | 幻灯片数组 |
| `layout_config` | JSON | 布局配置 |
| `theme` | VARCHAR(50) | 主题名称 |
| `custom_theme` | JSON | 自定义主题配置 |
| `target_audience` | VARCHAR(100) | 目标受众 |
| `presentation_type` | VARCHAR(50) | 类型: informative/persuasive/educational |
| `include_images` | BOOLEAN | 是否包含图片 |
| `image_style` | VARCHAR(50) | 图片风格 |
| `slide_count` | INTEGER | 幻灯片数量 |
| `thumbnail` | TEXT | Base64 缩略图 |
| `status` | VARCHAR(20) | 状态: draft/completed/archived |

**slides JSON 结构**:
```json
[
  {
    "type": "title",
    "title": "演示文稿标题",
    "subtitle": "副标题",
    "speaker_notes": "演讲者备注"
  },
  {
    "type": "content",
    "title": "内容页标题",
    "content": ["要点1", "要点2", "要点3"],
    "image_url": "https://...",
    "speaker_notes": "..."
  }
]
```

#### 10.5.2 slide_versions 表

存储幻灯片版本历史（用于回滚）。

```sql
CREATE TABLE slide_versions (
    id VARCHAR(36) PRIMARY KEY,
    presentation_id VARCHAR(36) NOT NULL,
    slide_index INTEGER NOT NULL,
    content JSON NOT NULL,
    layout VARCHAR(50),
    version_number INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX ix_slide_versions_presentation_id ON slide_versions(presentation_id);
```

---

### 10.6 数据库关系图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Auth Service Database                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────┐         ┌─────────────────────┐                   │
│  │     users       │ 1     n │   refresh_tokens    │                   │
│  ├─────────────────┤─────────├─────────────────────┤                   │
│  │ id (PK)         │         │ id (PK)             │                   │
│  │ username        │         │ user_id (FK)        │                   │
│  │ email           │         │ token_hash          │                   │
│  │ password_hash   │         │ expires_at          │                   │
│  │ is_active       │         │ is_revoked          │                   │
│  └─────────────────┘         └─────────────────────┘                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                         Chat Service Database                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────┐         ┌─────────────────────┐                   │
│  │  conversations  │ 1     n │     messages        │                   │
│  ├─────────────────┤─────────├─────────────────────┤                   │
│  │ id (PK)         │         │ id (PK)             │                   │
│  │ user_id         │         │ conversation_id (FK)│                   │
│  │ title           │         │ role                │                   │
│  │ model           │         │ content             │                   │
│  │ message_count   │         │ images (JSON)       │                   │
│  └─────────────────┘         │ tool_calls (JSON)   │                   │
│                              │ citations (JSON)    │                   │
│                              └─────────────────────┘                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                          RAG Service Database                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────┐         ┌─────────────────────┐                   │
│  │   documents     │ 1     n │      chunks         │                   │
│  ├─────────────────┤─────────├─────────────────────┤                   │
│  │ id (PK)         │         │ id (PK)             │                   │
│  │ user_id         │         │ document_id (FK)    │                   │
│  │ filename        │         │ user_id             │                   │
│  │ file_type       │         │ chunk_index         │                   │
│  │ chunk_count     │         │ content             │                   │
│  │ status          │         │ page_number         │                   │
│  └─────────────────┘         │ extra_data (JSON)   │                   │
│                              └─────────────────────┘                   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    document_vectors (pgvector)                   │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │ id (PK) | document_id | user_id | chunk_id | embedding (768)    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                     Presentation Service Database                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────┐         ┌─────────────────────┐                   │
│  │  presentations  │ 1     n │   slide_versions    │                   │
│  ├─────────────────┤─────────├─────────────────────┤                   │
│  │ id (PK)         │         │ id (PK)             │                   │
│  │ user_id         │         │ presentation_id     │                   │
│  │ title           │         │ slide_index         │                   │
│  │ slides (JSON)   │         │ content (JSON)      │                   │
│  │ theme           │         │ version_number      │                   │
│  │ status          │         │ created_at          │                   │
│  └─────────────────┘         └─────────────────────┘                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### 10.7 数据库迁移

#### 10.7.1 SQLAlchemy 自动迁移

项目使用 SQLAlchemy 的 `create_all()` 进行自动表创建：

```python
# database.py
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```

#### 10.7.2 手动迁移脚本

对于生产环境，建议使用 Alembic 进行版本化迁移：

```bash
# 安装 Alembic
pip install alembic

# 初始化
alembic init alembic

# 生成迁移脚本
alembic revision --autogenerate -m "Initial migration"

# 执行迁移
alembic upgrade head
```

---

### 10.8 数据库优化建议

#### 10.8.1 索引优化

```sql
-- 复合索引 (常用查询)
CREATE INDEX ix_messages_conv_created ON messages(conversation_id, created_at);
CREATE INDEX ix_chunks_doc_index ON chunks(document_id, chunk_index);

-- 部分索引 (状态过滤)
CREATE INDEX ix_documents_pending ON documents(user_id) WHERE status = 'pending';
```

#### 10.8.2 JSON 字段查询优化

```sql
-- PostgreSQL JSONB 索引
CREATE INDEX ix_messages_tool_calls ON messages USING GIN (tool_calls);

-- 查询示例
SELECT * FROM messages
WHERE tool_calls @> '[{"name": "rag_search"}]';
```

#### 10.8.3 向量检索优化

```sql
-- 增加 IVFFlat lists 数量 (数据量大时)
CREATE INDEX ix_vectors_embedding
ON document_vectors USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 1000);

-- 使用 HNSW 索引 (更快但占用更多内存)
CREATE INDEX ix_vectors_hnsw
ON document_vectors USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

#### 10.8.4 连接池配置

```python
# 生产环境连接池配置
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,           # 连接池大小
    max_overflow=10,        # 最大溢出连接
    pool_timeout=30,        # 获取连接超时
    pool_recycle=1800,      # 连接回收时间
    pool_pre_ping=True,     # 连接健康检查
)
```

---

### 10.9 数据备份与恢复

#### 10.9.1 PostgreSQL 备份

```bash
# 完整备份
pg_dump -h localhost -U postgres -d mydb > backup.sql

# 仅数据备份
pg_dump -h localhost -U postgres -d mydb --data-only > data_backup.sql

# 恢复
psql -h localhost -U postgres -d mydb < backup.sql
```

#### 10.9.2 Supabase 自动备份

Supabase 提供自动每日备份：
- Pro 计划: 7 天保留
- Team 计划: 14 天保留
- Enterprise: 自定义保留期

---

*(第十部分完成 - 数据库设计)*

