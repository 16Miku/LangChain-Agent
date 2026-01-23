# Plan-V9: 现代化前端重构与多模态增强

> **版本**: V9.0
> **日期**: 2025-12-31
> **目标**: 使用 Next.js 重构前端，集成多模态能力，增强 RAG 检索，引入用户认证系统
> **状态**: 🚧 开发中 (Phase 3: Week 7)

---

## 📑 目录

1. [版本概述](#一版本概述)
2. [需求规格说明](#二需求规格说明)
3. [系统架构设计](#三系统架构设计)
4. [模块详细设计](#四模块详细设计)
5. [数据库设计](#五数据库设计)
6. [API 接口设计](#六api-接口设计)
7. [前端页面设计](#七前端页面设计)
8. [部署架构](#八部署架构)
9. [开发计划](#九开发计划)
10. [风险评估与应对](#十风险评估与应对)
11. [验收标准](#十一验收标准)
12. [附录](#十二附录)
   - 12.1 [参考资料](#121-参考资料)
   - 12.2 [术语表](#122-术语表)
   - 12.3 [变更历史](#123-变更历史)

---

## 一、版本概述

### 1.1 版本目标

V9.0 是 My-Chat-LangChain 项目的重大升级版本，核心目标是：

1. **前端现代化**: 使用 Next.js + shadcn/ui 完全重构前端，替代 Streamlit
2. **多模态交互**: 支持图片理解/OCR 和语音交互
3. **RAG 能力增强**: 混合检索、引用追溯、重排序、MinerU 文档解析
4. **用户系统**: 传统账号认证 + JWT
5. **生产级部署**: Docker Compose 一键部署

### 1.2 版本对比

```
V8.0 (当前)                              V9.0 (目标)
├── Streamlit 前端                        ├── Next.js 14 + shadcn/ui 前端
├── 无用户系统                            ├── 完整用户认证系统 (JWT)
├── ChromaDB 向量存储                     ├── Milvus 向量数据库
├── SQLite 持久化                         ├── PostgreSQL 用户数据库
├── 文本聊天                              ├── 文本 + 图片 + 语音 多模态
├── 基础 RAG 检索                         ├── 混合检索 + 重排序 + 引用追溯
├── 手动文件上传解析                       ├── MinerU 智能文档解析
├── 单容器部署                            ├── Docker Compose 微服务部署
└── 96+ 工具                              └── 96+ 工具 (保持)
```

### 1.3 核心功能清单

| 功能模块 | 子功能 | 优先级 | 阶段 |
|---------|--------|--------|------|
| **Next.js 前端** | 聊天界面 | P0 | Phase 1 |
| | 消息流式渲染 | P0 | Phase 1 |
| | 工具调用可视化 | P0 | Phase 1 |
| | 图表/图片渲染 | P0 | Phase 1 |
| | 响应式设计 | P1 | Phase 1 |
| | 暗色模式 | P2 | Phase 1 |
| **用户系统** | 注册/登录 | P0 | Phase 1 |
| | JWT 认证 | P0 | Phase 1 |
| | 会话管理 | P0 | Phase 1 |
| | 用户设置 | P1 | Phase 1 |
| | API Key 管理 | P1 | Phase 1 |
| **多模态** | 图片上传与理解 | P0 | Phase 2 |
| | OCR 文字识别 | P1 | Phase 2 |
| | 语音输入 (Whisper) | P1 | Phase 2 |
| | 语音输出 (Edge TTS) | P2 | Phase 2 |
| **RAG 增强** | Milvus 向量存储迁移 | P0 | Phase 3 |
| | 混合检索 (向量+BM25) | P0 | Phase 3 |
| | 引用追溯 | P0 | Phase 3 |
| | Reranker 重排序 | P1 | Phase 3 |
| | MinerU 文档解析 | P1 | Phase 3 |
| | 多轮对话检索 | P2 | Phase 3 |
| **部署** | Docker Compose | P0 | Phase 1 |
| | 环境配置管理 | P0 | Phase 1 |
| | 健康检查 | P1 | Phase 1 |

---

## 二、需求规格说明

### 2.1 功能需求

#### 2.1.1 Next.js 前端 (FR-01)

**FR-01-01: 对话式聊天界面**
- 类似 ChatGPT 的对话 UI 风格
- 支持 Markdown 渲染（代码高亮、表格、列表等）
- 支持 LaTeX 数学公式渲染
- 消息气泡区分用户/AI
- 支持消息复制、重新生成
- 输入框支持多行、快捷键发送

**FR-01-02: 流式响应渲染**
- 实时显示 AI 回复（SSE/WebSocket）
- 打字机效果逐字显示
- 支持中断生成
- 加载状态指示

**FR-01-03: 工具调用可视化**
- 折叠式工具调用面板
- 显示工具名称、参数、耗时
- 工具执行状态指示（进行中/成功/失败）
- 工具输出智能摘要（非原始 JSON）

**FR-01-04: 多媒体渲染**
- 图表渲染（Base64 图片）
- 代码块语法高亮
- 表格响应式显示
- 外部图片懒加载

**FR-01-05: 侧边栏功能**
- 会话历史列表
- 新建/删除/重命名会话
- 会话搜索
- 用户设置入口
- API Key 配置

**FR-01-06: 响应式设计**
- 桌面端完整功能
- 移动端自适应布局
- 侧边栏可折叠

#### 2.1.2 用户认证系统 (FR-02)

**FR-02-01: 用户注册**
- 用户名 + 邮箱 + 密码注册
- 密码强度验证
- 用户名/邮箱唯一性检查
- 注册成功自动登录

**FR-02-02: 用户登录**
- 用户名/邮箱 + 密码登录
- JWT Token 生成与验证
- 记住登录状态（Refresh Token）
- 登录失败次数限制

**FR-02-03: 会话管理**
- Token 自动刷新
- 多设备登录支持
- 强制登出功能
- 会话过期提示

**FR-02-04: 用户设置**
- 修改密码
- 修改用户名/邮箱
- 个人 API Key 管理
- 偏好设置（主题、语言等）

**FR-02-05: 权限控制**
- 未登录：仅可访问登录/注册页
- 已登录：完整功能访问
- API 请求 Token 验证

#### 2.1.3 多模态能力 (FR-03)

**FR-03-01: 图片理解**
- 支持上传图片（JPG/PNG/GIF/WebP）
- 支持粘贴剪贴板图片
- 支持拖拽上传
- 图片预览与删除
- 调用 Gemini Vision API 分析图片
- 支持多图同时上传

**FR-03-02: OCR 文字识别**
- 识别图片中的文字
- 支持中英文混合识别
- 返回结构化文本

**FR-03-03: 语音输入**
- 录音按钮（按住录音/点击切换）
- 本地 Whisper 语音识别
- 识别结果填入输入框
- 支持中文/英文/混合语音

**FR-03-04: 语音输出**
- AI 回复文字转语音
- Edge TTS 语音合成
- 播放/暂停控制
- 语音选择（声音类型）

#### 2.1.4 RAG 增强 (FR-04)

**FR-04-01: Milvus 向量存储**
- 迁移 ChromaDB 至 Milvus
- 支持大规模向量存储
- 高性能相似度搜索
- Collection 管理

**FR-04-02: 混合检索**
- 向量相似度检索
- BM25 关键词检索
- RRF (Reciprocal Rank Fusion) 融合
- 可配置检索权重

**FR-04-03: 引用追溯**
- 每段回复标注来源文档
- 显示具体页码/章节
- 点击引用跳转原文
- 引用置信度评分

**FR-04-04: 结果重排序**
- 使用 Reranker 模型（如 bge-reranker）
- 对检索结果二次排序
- 提升相关性准确度

**FR-04-05: MinerU 文档解析**
- 调用 MinerU 云服务 API
- 支持 PDF/Word/PPT 等格式
- 智能分块（语义切分）
- 表格/图表提取
- 公式识别

**FR-04-06: 多轮对话检索**
- 对话历史上下文理解
- 查询改写（Query Rewriting）
- 追问场景优化

#### 2.1.5 部署与运维 (FR-05)

**FR-05-01: Docker Compose 部署**
- 一键启动所有服务
- 服务依赖管理
- 网络隔离配置
- 数据卷持久化

**FR-05-02: 环境配置**
- 环境变量统一管理
- 开发/生产环境分离
- 敏感信息加密

**FR-05-03: 健康检查**
- 服务存活检查
- 依赖服务检查
- 自动重启策略

### 2.2 非功能需求

#### 2.2.1 性能需求 (NFR-01)

| 指标 | 目标值 |
|------|--------|
| 首屏加载时间 | < 2s |
| 消息发送响应 | < 500ms |
| 流式首 Token | < 1s |
| RAG 检索延迟 | < 500ms |
| 并发用户数 | 100+ |

#### 2.2.2 安全需求 (NFR-02)

- 密码 bcrypt 加密存储
- JWT Token 签名验证
- HTTPS 传输加密
- SQL 注入防护
- XSS 防护
- CORS 配置

#### 2.2.3 可用性需求 (NFR-03)

- 服务可用性 > 99%
- 优雅降级（外部服务故障时）
- 错误提示用户友好

#### 2.2.4 可维护性需求 (NFR-04)

- 代码规范一致
- 完整的错误日志
- API 文档自动生成
- 单元测试覆盖率 > 60%

---

## 三、系统架构设计

### 3.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           My-Chat-LangChain V9.0                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        Frontend (Next.js 14)                         │   │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────────────┐    │   │
│  │  │ Chat Page │ │Login/Reg  │ │ Settings  │ │ Conversation List │    │   │
│  │  └───────────┘ └───────────┘ └───────────┘ └───────────────────┘    │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │                    shadcn/ui + Tailwind                      │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                          HTTP/REST + SSE                                    │
│                                    │                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        API Gateway (Nginx)                           │   │
│  │                    - 反向代理 - SSL 终止 - 负载均衡                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│          ┌─────────────────────────┼─────────────────────────┐              │
│          │                         │                         │              │
│          ▼                         ▼                         ▼              │
│  ┌───────────────┐        ┌───────────────┐        ┌───────────────┐       │
│  │  Auth Service │        │  Chat Service │        │  RAG Service  │       │
│  │  (FastAPI)    │        │  (FastAPI)    │        │  (FastAPI)    │       │
│  │               │        │               │        │               │       │
│  │ - 用户注册    │        │ - 聊天流式    │        │ - 文档解析    │       │
│  │ - 用户登录    │        │ - Agent 调用  │        │ - 向量检索    │       │
│  │ - Token 管理  │        │ - 工具执行    │        │ - 混合检索    │       │
│  │ - 权限验证    │        │ - 会话管理    │        │ - 重排序      │       │
│  └───────┬───────┘        └───────┬───────┘        └───────┬───────┘       │
│          │                         │                         │              │
│          │                         │                         │              │
│          ▼                         ▼                         ▼              │
│  ┌───────────────────────────────────────────────────────────────────┐     │
│  │                         Data Layer                                 │     │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────┐ │     │
│  │  │ PostgreSQL  │  │   Milvus    │  │    Redis    │  │ MinIO/S3 │ │     │
│  │  │ - 用户数据  │  │ - 向量存储  │  │ - 会话缓存  │  │ - 文件   │ │     │
│  │  │ - 会话记录  │  │ - 相似搜索  │  │ - Token     │  │   存储   │ │     │
│  │  │ - 设置配置  │  │             │  │             │  │          │ │     │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └──────────┘ │     │
│  └───────────────────────────────────────────────────────────────────┘     │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐     │
│  │                       External Services                            │     │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────┐ │     │
│  │  │ Gemini  │ │  E2B    │ │  MCP    │ │ MinerU  │ │ Whisper     │ │     │
│  │  │ Vision  │ │ Sandbox │ │ Tools   │ │  API    │ │ (Local)     │ │     │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────────┘ │     │
│  └───────────────────────────────────────────────────────────────────┘     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 服务拆分

| 服务 | 职责 | 技术栈 | 端口 |
|------|------|--------|------|
| **frontend** | Next.js 前端应用 | Next.js 14, React 18, shadcn/ui | 3000 |
| **auth-service** | 用户认证服务 | FastAPI, SQLAlchemy | 8001 |
| **chat-service** | 聊天核心服务 | FastAPI, LangGraph | 8002 |
| **rag-service** | RAG 检索服务 | FastAPI, LangChain | 8004 |
| **whisper-service** | 语音识别服务 | FastAPI, faster-whisper | 8003 |
| **nginx** | API 网关 | Nginx | 80/443 |
| **postgres** | 关系数据库 | PostgreSQL 15 | 5432 |
| **milvus** | 向量数据库 | Milvus 2.x | 19530 |
| **redis** | 缓存/会话 | Redis 7 | 6379 |
| **minio** | 文件存储 | MinIO | 9000 |

### 3.3 服务间通信

```
┌─────────────┐     HTTP/REST      ┌─────────────┐
│   Frontend  │ ◄──────────────────► │   Nginx     │
└─────────────┘                     └──────┬──────┘
                                           │
                        ┌──────────────────┼──────────────────┐
                        │                  │                  │
                        ▼                  ▼                  ▼
                ┌───────────────┐  ┌───────────────┐  ┌───────────────┐
                │ Auth Service  │  │ Chat Service  │  │  RAG Service  │
                └───────┬───────┘  └───────┬───────┘  └───────┬───────┘
                        │                  │                  │
                        │    Internal gRPC/HTTP              │
                        │                  │                  │
                        ▼                  ▼                  ▼
                ┌─────────────────────────────────────────────────────┐
                │                    Data Layer                        │
                │  PostgreSQL │ Milvus │ Redis │ MinIO                │
                └─────────────────────────────────────────────────────┘
```

### 3.4 技术选型详解

| 类别 | 技术 | 版本 | 选型理由 |
|------|------|------|---------|
| **前端框架** | Next.js | 14.x | App Router、SSR、API Routes |
| **UI 组件库** | shadcn/ui | latest | 可定制、现代、与 Tailwind 集成 |
| **CSS 框架** | Tailwind CSS | 3.x | 原子化 CSS、响应式 |
| **状态管理** | Zustand | 4.x | 轻量、简洁、TypeScript 友好 |
| **HTTP 客户端** | Axios | 1.x | 拦截器、请求取消 |
| **后端框架** | FastAPI | 0.115+ | 异步、自动文档、类型安全 |
| **ORM** | SQLAlchemy | 2.x | 成熟、功能全面 |
| **认证** | python-jose | 3.x | JWT 处理 |
| **密码加密** | passlib[bcrypt] | 1.7+ | 行业标准 |
| **向量数据库** | Milvus | 2.x | 高性能、分布式、功能丰富 |
| **关系数据库** | PostgreSQL | 15.x | 稳定、功能强大 |
| **缓存** | Redis | 7.x | 高性能、会话存储 |
| **文件存储** | MinIO | latest | S3 兼容、自托管 |
| **语音识别** | faster-whisper | 1.x | 本地运行、高精度 |
| **语音合成** | edge-tts | 6.x | 免费、高质量 |
| **文档解析** | MinerU API | - | 智能分块、OCR |
| **容器编排** | Docker Compose | 2.x | 简单部署 |

---

## 四、模块详细设计

### 4.1 前端模块设计

#### 4.1.1 项目结构

```
frontend/
├── app/                          # Next.js App Router
│   ├── (auth)/                   # 认证相关路由组
│   │   ├── login/
│   │   │   └── page.tsx
│   │   ├── register/
│   │   │   └── page.tsx
│   │   └── layout.tsx
│   ├── (main)/                   # 主应用路由组
│   │   ├── chat/
│   │   │   ├── [id]/
│   │   │   │   └── page.tsx      # 单个会话页面
│   │   │   └── page.tsx          # 新会话页面
│   │   ├── settings/
│   │   │   └── page.tsx
│   │   └── layout.tsx            # 带侧边栏的布局
│   ├── api/                      # API Routes (可选)
│   │   └── auth/
│   │       └── [...nextauth]/
│   │           └── route.ts
│   ├── layout.tsx                # 根布局
│   ├── page.tsx                  # 首页（重定向到 /chat）
│   └── globals.css
├── components/
│   ├── chat/
│   │   ├── ChatContainer.tsx     # 聊天容器
│   │   ├── MessageList.tsx       # 消息列表
│   │   ├── MessageBubble.tsx     # 单条消息气泡
│   │   ├── InputArea.tsx         # 输入区域
│   │   ├── ToolCallPanel.tsx     # 工具调用面板
│   │   ├── CodeBlock.tsx         # 代码块组件
│   │   ├── ImageUploader.tsx     # 图片上传
│   │   └── VoiceRecorder.tsx     # 语音录制
│   ├── sidebar/
│   │   ├── Sidebar.tsx           # 侧边栏主组件
│   │   ├── ConversationList.tsx  # 会话列表
│   │   ├── ConversationItem.tsx  # 单个会话项
│   │   └── UserMenu.tsx          # 用户菜单
│   ├── settings/
│   │   ├── SettingsPanel.tsx
│   │   ├── APIKeyForm.tsx
│   │   └── ThemeSelector.tsx
│   ├── ui/                       # shadcn/ui 组件
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── dialog.tsx
│   │   └── ...
│   └── providers/
│       ├── AuthProvider.tsx
│       └── ThemeProvider.tsx
├── lib/
│   ├── api/
│   │   ├── client.ts             # Axios 客户端
│   │   ├── auth.ts               # 认证 API
│   │   ├── chat.ts               # 聊天 API
│   │   └── rag.ts                # RAG API
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useChat.ts
│   │   ├── useSSE.ts             # SSE 流式处理
│   │   └── useVoice.ts
│   ├── stores/
│   │   ├── authStore.ts          # Zustand 认证状态
│   │   ├── chatStore.ts          # 聊天状态
│   │   └── settingsStore.ts      # 设置状态
│   ├── utils/
│   │   ├── markdown.ts           # Markdown 处理
│   │   ├── format.ts             # 格式化工具
│   │   └── storage.ts            # 本地存储
│   └── types/
│       ├── auth.ts
│       ├── chat.ts
│       └── api.ts
├── public/
│   └── ...
├── tailwind.config.ts
├── next.config.js
├── package.json
└── tsconfig.json
```

#### 4.1.2 核心组件设计

**MessageBubble 组件**

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
  toolCalls?: ToolCall[];
  images?: string[];      // Base64 图片
  citations?: Citation[]; // 引用来源
}

interface ToolCall {
  id: string;
  name: string;
  args: Record<string, any>;
  status: 'running' | 'success' | 'error';
  output?: string;
  duration?: number;
}

interface Citation {
  sourceId: string;
  sourceName: string;
  pageNumber?: number;
  content: string;
  confidence: number;
}
```

**InputArea 组件**

```typescript
// components/chat/InputArea.tsx

interface InputAreaProps {
  onSend: (message: string, images?: File[]) => void;
  onVoiceInput: (transcript: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

// 功能:
// - 多行文本输入 (Shift+Enter 换行, Enter 发送)
// - 图片上传按钮 (支持多选)
// - 图片拖拽上传
// - 图片粘贴 (Ctrl+V)
// - 语音录制按钮
// - 发送按钮
// - 已选图片预览条
```

#### 4.1.3 状态管理

**认证状态 (authStore.ts)**

```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;

  login: (email: string, password: string) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  refreshAccessToken: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (email, password) => { /* ... */ },
      register: async (data) => { /* ... */ },
      logout: () => { /* ... */ },
      refreshAccessToken: async () => { /* ... */ },
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

**聊天状态 (chatStore.ts)**

```typescript
interface ChatState {
  conversations: Conversation[];
  currentConversationId: string | null;
  messages: Message[];
  isStreaming: boolean;

  // Actions
  createConversation: () => Promise<string>;
  loadConversation: (id: string) => Promise<void>;
  deleteConversation: (id: string) => Promise<void>;
  sendMessage: (content: string, images?: File[]) => Promise<void>;
  stopStreaming: () => void;
  regenerateMessage: (messageId: string) => Promise<void>;
}
```

### 4.2 后端模块设计

#### 4.2.1 Auth Service

```
backend/auth-service/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 应用入口
│   ├── config.py               # 配置管理
│   ├── database.py             # 数据库连接
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py             # 用户模型
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py             # 用户 Schema
│   │   └── token.py            # Token Schema
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py         # 认证路由
│   │       └── users.py        # 用户路由
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py         # 密码加密、Token 生成
│   │   └── deps.py             # 依赖注入
│   └── services/
│       ├── __init__.py
│       └── user_service.py     # 用户业务逻辑
├── requirements.txt
└── Dockerfile
```

**核心接口:**

```python
# app/api/v1/auth.py

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    pass

@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """用户登录"""
    pass

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str):
    """刷新 Access Token"""
    pass

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """用户登出"""
    pass
```

#### 4.2.2 Chat Service (现有改造)

```
backend/chat-service/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 入口 (原 backend/main.py)
│   ├── config.py
│   ├── agent_service.py        # Agent 核心 (保持)
│   ├── models/
│   │   ├── conversation.py     # 会话模型
│   │   └── message.py          # 消息模型
│   ├── schemas/
│   │   ├── chat.py
│   │   └── tool.py
│   ├── api/
│   │   └── v1/
│   │       ├── chat.py         # 聊天路由
│   │       ├── conversation.py # 会话管理
│   │       └── upload.py       # 文件上传
│   └── tools/                  # 工具集 (保持)
│       ├── e2b_tools.py
│       ├── rag_tools.py
│       └── search_tools.py
├── requirements.txt
└── Dockerfile
```

**聊天 API 改造:**

```python
# app/api/v1/chat.py

@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """流式聊天 (需要认证)"""
    return StreamingResponse(
        generate_stream(request, current_user),
        media_type="text/event-stream"
    )

@router.get("/conversations")
async def list_conversations(
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 20
):
    """获取用户会话列表"""
    pass

@router.post("/conversations")
async def create_conversation(
    current_user: User = Depends(get_current_user)
):
    """创建新会话"""
    pass

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user)
):
    """删除会话"""
    pass
```

#### 4.2.3 RAG Service

```
backend/rag-service/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── milvus_client.py        # Milvus 客户端
│   ├── models/
│   │   ├── document.py
│   │   └── chunk.py
│   ├── schemas/
│   │   ├── document.py
│   │   └── search.py
│   ├── api/
│   │   └── v1/
│   │       ├── documents.py    # 文档管理
│   │       ├── search.py       # 检索接口
│   │       └── ingest.py       # 文档摄取
│   └── services/
│       ├── embedding_service.py
│       ├── search_service.py   # 混合检索
│       ├── rerank_service.py   # 重排序
│       └── mineru_service.py   # MinerU 集成
├── requirements.txt
└── Dockerfile
```

**混合检索实现:**

```python
# app/services/search_service.py

class HybridSearchService:
    def __init__(self, milvus_client, bm25_index, reranker):
        self.milvus = milvus_client
        self.bm25 = bm25_index
        self.reranker = reranker

    async def search(
        self,
        query: str,
        top_k: int = 10,
        alpha: float = 0.5,  # 向量权重
        rerank: bool = True
    ) -> List[SearchResult]:
        """混合检索"""
        # 1. 向量检索
        vector_results = await self.milvus.search(
            query_embedding=self.embed(query),
            top_k=top_k * 2
        )

        # 2. BM25 关键词检索
        bm25_results = self.bm25.search(query, top_k=top_k * 2)

        # 3. RRF 融合
        fused_results = self.rrf_fusion(
            vector_results, bm25_results, alpha=alpha
        )

        # 4. Reranker 重排序 (可选)
        if rerank:
            fused_results = await self.reranker.rerank(
                query, fused_results, top_k=top_k
            )

        return fused_results[:top_k]

    def rrf_fusion(self, vec_results, bm25_results, alpha=0.5):
        """Reciprocal Rank Fusion"""
        scores = {}
        k = 60  # RRF 常数

        for rank, doc in enumerate(vec_results):
            scores[doc.id] = scores.get(doc.id, 0) + alpha / (k + rank)

        for rank, doc in enumerate(bm25_results):
            scores[doc.id] = scores.get(doc.id, 0) + (1-alpha) / (k + rank)

        return sorted(scores.items(), key=lambda x: x[1], reverse=True)
```

#### 4.2.4 Whisper Service

```
backend/whisper-service/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   └── api/
│       └── v1/
│           └── transcribe.py
├── requirements.txt
└── Dockerfile
```

```python
# app/api/v1/transcribe.py

from faster_whisper import WhisperModel

model = WhisperModel("base", device="cpu", compute_type="int8")

@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str = "zh"
):
    """语音转文字"""
    audio_bytes = await file.read()
    segments, info = model.transcribe(
        audio_bytes,
        language=language,
        beam_size=5
    )

    text = "".join([segment.text for segment in segments])
    return {"text": text, "language": info.language}
```

### 4.3 多模态处理流程

#### 4.3.1 图片理解流程

```
用户上传图片
     │
     ▼
┌─────────────────┐
│ 前端预处理      │
│ - 压缩图片      │
│ - 转 Base64     │
│ - 预览显示      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 发送到后端      │
│ POST /chat/stream│
│ {               │
│   content: "...",│
│   images: [...]  │
│ }               │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ Agent Service                        │
│ 1. 构建多模态消息                    │
│ 2. 调用 Gemini Vision API            │
│    - 图片分析                        │
│    - 结合文本 prompt                 │
│ 3. 流式返回结果                      │
└─────────────────────────────────────┘
```

**多模态消息构建:**

```python
# agent_service.py

def build_multimodal_message(content: str, images: List[str]) -> dict:
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

#### 4.3.2 语音交互流程

```
                        语音输入流程
┌──────────────────────────────────────────────────────────────┐
│ 用户点击录音                                                   │
│      │                                                        │
│      ▼                                                        │
│ ┌─────────────────┐                                          │
│ │ 浏览器录音 API   │                                          │
│ │ MediaRecorder   │                                          │
│ └────────┬────────┘                                          │
│          │ 录音结束                                            │
│          ▼                                                    │
│ ┌─────────────────┐     POST /api/whisper/transcribe         │
│ │ 上传音频文件     │ ─────────────────────────────────────►    │
│ └─────────────────┘                                          │
│          │                                                    │
│          │   ┌────────────────────────────────────────────┐  │
│          │   │ Whisper Service                            │  │
│          │   │ - faster-whisper 识别                      │  │
│          │   │ - 返回文字                                  │  │
│          │   └────────────────────────────────────────────┘  │
│          │                                                    │
│          ▼                                                    │
│ ┌─────────────────┐                                          │
│ │ 填入输入框       │                                          │
│ │ (可编辑确认)     │                                          │
│ └─────────────────┘                                          │
└──────────────────────────────────────────────────────────────┘

                        语音输出流程
┌──────────────────────────────────────────────────────────────┐
│ AI 回复完成                                                    │
│      │                                                        │
│      ▼                                                        │
│ ┌─────────────────┐     POST /api/tts/synthesize              │
│ │ 请求语音合成     │ ─────────────────────────────────────►    │
│ └─────────────────┘                                          │
│          │                                                    │
│          │   ┌────────────────────────────────────────────┐  │
│          │   │ TTS Service (Edge TTS)                     │  │
│          │   │ - 文字转语音                                │  │
│          │   │ - 返回音频流                                │  │
│          │   └────────────────────────────────────────────┘  │
│          │                                                    │
│          ▼                                                    │
│ ┌─────────────────┐                                          │
│ │ Audio 播放器     │                                          │
│ │ - 播放/暂停     │                                          │
│ │ - 进度条        │                                          │
│ └─────────────────┘                                          │
└──────────────────────────────────────────────────────────────┘
```

---

## 五、数据库设计

### 5.1 PostgreSQL Schema

```sql
-- 用户表
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 用户设置表
CREATE TABLE user_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    theme VARCHAR(20) DEFAULT 'system',
    language VARCHAR(10) DEFAULT 'zh-CN',
    voice_enabled BOOLEAN DEFAULT FALSE,
    default_model VARCHAR(50) DEFAULT 'gemini-2.0-flash-lite',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- API Key 表
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    key_name VARCHAR(100) NOT NULL,
    key_type VARCHAR(50) NOT NULL,  -- 'google', 'e2b', 'openai', etc.
    encrypted_value TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, key_type)
);

-- 会话表
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) DEFAULT 'New Chat',
    model VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 消息表
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,  -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    images JSONB,               -- 图片 URL/Base64 数组
    tool_calls JSONB,           -- 工具调用记录
    citations JSONB,            -- 引用来源
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 文档表 (RAG)
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50),
    file_size INTEGER,
    milvus_collection VARCHAR(100),
    chunk_count INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'processing', 'ready', 'error'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Refresh Token 表
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_documents_user_id ON documents(user_id);
CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
```

### 5.2 Milvus Schema

```python
# Collection: document_chunks

from pymilvus import CollectionSchema, FieldSchema, DataType

fields = [
    FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=36),
    FieldSchema(name="document_id", dtype=DataType.VARCHAR, max_length=36),
    FieldSchema(name="user_id", dtype=DataType.VARCHAR, max_length=36),
    FieldSchema(name="chunk_index", dtype=DataType.INT64),
    FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
    FieldSchema(name="page_number", dtype=DataType.INT64),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=384),  # all-MiniLM-L6-v2
    FieldSchema(name="metadata", dtype=DataType.JSON),
]

schema = CollectionSchema(
    fields=fields,
    description="Document chunks for RAG"
)

# Index
index_params = {
    "metric_type": "IP",  # Inner Product (cosine similarity)
    "index_type": "IVF_FLAT",
    "params": {"nlist": 1024}
}
```

### 5.3 Redis 数据结构

```
# Session 存储
session:{user_id} -> Hash
  - access_token: string
  - refresh_token: string
  - created_at: timestamp
  - last_active: timestamp

# Rate Limiting
rate_limit:{user_id}:{endpoint} -> Counter
  - expire: 60s

# Token 黑名单
blacklist:{token_hash} -> Set
  - expire: token 剩余有效期
```

---

## 六、API 接口设计

### 6.1 认证接口

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| POST | /api/auth/register | 用户注册 | 否 |
| POST | /api/auth/login | 用户登录 | 否 |
| POST | /api/auth/refresh | 刷新 Token | 否 |
| POST | /api/auth/logout | 用户登出 | 是 |
| GET | /api/auth/me | 获取当前用户 | 是 |
| PUT | /api/auth/password | 修改密码 | 是 |

**请求/响应示例:**

```yaml
# POST /api/auth/register
Request:
  {
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123!"
  }

Response: 201
  {
    "id": "uuid",
    "username": "john_doe",
    "email": "john@example.com",
    "created_at": "2025-12-31T00:00:00Z"
  }

# POST /api/auth/login
Request:
  {
    "email": "john@example.com",
    "password": "SecurePass123!"
  }

Response: 200
  {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 3600
  }
```

### 6.2 聊天接口

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| GET | /api/conversations | 获取会话列表 | 是 |
| POST | /api/conversations | 创建会话 | 是 |
| GET | /api/conversations/{id} | 获取会话详情 | 是 |
| PUT | /api/conversations/{id} | 更新会话 | 是 |
| DELETE | /api/conversations/{id} | 删除会话 | 是 |
| GET | /api/conversations/{id}/messages | 获取消息列表 | 是 |
| POST | /api/chat/stream | 流式聊天 | 是 |
| POST | /api/chat/stop | 停止生成 | 是 |

**流式聊天请求:**

```yaml
# POST /api/chat/stream
Request:
  {
    "conversation_id": "uuid",
    "content": "分析这张图片",
    "images": ["base64..."],  # 可选
    "api_keys": {             # 可选，覆盖用户默认配置
      "GOOGLE_API_KEY": "..."
    }
  }

Response: SSE Stream
  event: text
  data: {"content": "这是一张..."}

  event: tool_start
  data: {"tool_name": "search_engine", "tool_id": "xxx"}

  event: tool_end
  data: {"tool_id": "xxx", "output": "...", "duration": 1.5}

  event: citation
  data: {"source": "doc.pdf", "page": 5, "content": "..."}

  event: done
  data: {"message_id": "uuid", "total_tokens": 1500}
```

### 6.3 RAG 接口

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| GET | /api/documents | 获取文档列表 | 是 |
| POST | /api/documents/upload | 上传文档 | 是 |
| DELETE | /api/documents/{id} | 删除文档 | 是 |
| GET | /api/documents/{id}/status | 获取处理状态 | 是 |
| POST | /api/search | 检索文档 | 是 |

**文档上传:**

```yaml
# POST /api/documents/upload
Request: multipart/form-data
  - file: binary
  - parse_method: "mineru" | "default"

Response: 202
  {
    "document_id": "uuid",
    "filename": "report.pdf",
    "status": "processing",
    "estimated_time": 30
  }
```

### 6.4 语音接口

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| POST | /api/voice/transcribe | 语音转文字 | 是 |
| POST | /api/voice/synthesize | 文字转语音 | 是 |

```yaml
# POST /api/voice/transcribe
Request: multipart/form-data
  - audio: binary (wav/mp3/webm)
  - language: "zh" | "en" | "auto"

Response: 200
  {
    "text": "识别的文字内容",
    "language": "zh",
    "confidence": 0.95
  }

# POST /api/voice/synthesize
Request:
  {
    "text": "要转换的文字",
    "voice": "zh-CN-XiaoxiaoNeural",
    "rate": 1.0,
    "pitch": 0
  }

Response: audio/mpeg (binary stream)
```

### 6.5 用户设置接口

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| GET | /api/settings | 获取用户设置 | 是 |
| PUT | /api/settings | 更新用户设置 | 是 |
| GET | /api/settings/api-keys | 获取 API Key 列表 | 是 |
| POST | /api/settings/api-keys | 添加 API Key | 是 |
| DELETE | /api/settings/api-keys/{type} | 删除 API Key | 是 |

---

## 七、前端页面设计

### 7.1 页面结构

```
/                           → 重定向到 /chat
/login                      → 登录页
/register                   → 注册页
/chat                       → 新会话（主页面）
/chat/[id]                  → 指定会话
/settings                   → 用户设置
/settings/api-keys          → API Key 管理
/settings/profile           → 个人资料
```

### 7.2 主页面布局 (Desktop)

```
┌─────────────────────────────────────────────────────────────────────┐
│                           Header                                     │
│  ┌──────────────────┐                         ┌────────────────────┐│
│  │ 🤖 Stream-Agent  │                         │ 👤 User ▼         ││
│  └──────────────────┘                         └────────────────────┘│
├─────────────────────────────────────────────────────────────────────┤
│┌──────────────────┐ ┌──────────────────────────────────────────────┐│
││                  │ │                                              ││
││   Sidebar        │ │              Chat Area                       ││
││                  │ │                                              ││
││  ┌─────────────┐ │ │  ┌──────────────────────────────────────────┐││
││  │ + New Chat  │ │ │  │                                          │││
││  └─────────────┘ │ │  │         Message List                     │││
││                  │ │  │                                          │││
││  Search...       │ │  │  ┌────────────────────────────────────┐  │││
││                  │ │  │  │ 👤 User: 你好                      │  │││
││  ┌─────────────┐ │ │  │  └────────────────────────────────────┘  │││
││  │ Today       │ │ │  │                                          │││
││  │ - Chat 1    │ │ │  │  ┌────────────────────────────────────┐  │││
││  │ - Chat 2    │ │ │  │  │ 🤖 AI: 你好！有什么...            │  │││
││  │             │ │ │  │  │                                    │  │││
││  │ Yesterday   │ │ │  │  │ ┌────────────────────────────────┐│  │││
││  │ - Chat 3    │ │ │  │  │ │ 🔧 Tool: search_engine        ││  │││
││  │             │ │ │  │  │ │    Status: ✅                 ││  │││
││  └─────────────┘ │ │  │  │ └────────────────────────────────┘│  │││
││                  │ │  │  └────────────────────────────────────┘  │││
││                  │ │  │                                          │││
││  ┌─────────────┐ │ │  └──────────────────────────────────────────┘││
││  │ ⚙️ Settings │ │ │                                              ││
││  └─────────────┘ │ │  ┌──────────────────────────────────────────┐││
│└──────────────────┘ │  │              Input Area                   │││
│                     │  │ ┌──────┐ ┌───────────────────┐ ┌───────┐ │││
│                     │  │ │ 📎   │ │ Message...        │ │ 🎤 ➤ │ │││
│                     │  │ └──────┘ └───────────────────┘ └───────┘ │││
│                     │  └──────────────────────────────────────────┘││
│                     └──────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────┘
```

### 7.3 移动端布局

```
┌─────────────────────────┐
│ ☰   Stream-Agent   👤   │
├─────────────────────────┤
│                         │
│    Message List         │
│                         │
│  ┌───────────────────┐  │
│  │ 👤 你好           │  │
│  └───────────────────┘  │
│                         │
│  ┌───────────────────┐  │
│  │ 🤖 你好！有什么...│  │
│  │                   │  │
│  │ [🔧 Tool ▼]      │  │
│  └───────────────────┘  │
│                         │
├─────────────────────────┤
│ 📎 │ Message...    │🎤➤│
└─────────────────────────┘
```

### 7.4 组件样式规范

**颜色系统 (shadcn/ui + Tailwind):**

```css
/* globals.css */
@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
    --primary: 221.2 83.2% 53.3%;
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96.1%;
    --muted: 210 40% 96.1%;
    --accent: 210 40% 96.1%;
    --destructive: 0 84.2% 60.2%;
    --border: 214.3 31.8% 91.4%;
    --ring: 221.2 83.2% 53.3%;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --card: 222.2 84% 4.9%;
    --card-foreground: 210 40% 98%;
    --primary: 217.2 91.2% 59.8%;
    --secondary: 217.2 32.6% 17.5%;
    --muted: 217.2 32.6% 17.5%;
    --accent: 217.2 32.6% 17.5%;
    --destructive: 0 62.8% 30.6%;
    --border: 217.2 32.6% 17.5%;
  }
}
```

**消息气泡样式:**

```typescript
// 用户消息
<div className="flex justify-end">
  <div className="max-w-[80%] rounded-2xl bg-primary text-primary-foreground px-4 py-2">
    {content}
  </div>
</div>

// AI 消息
<div className="flex justify-start">
  <div className="max-w-[80%] rounded-2xl bg-muted px-4 py-2">
    {content}
  </div>
</div>
```

---

## 八、部署架构

### 8.1 Docker Compose 配置

```yaml
# docker-compose.yml

version: '3.8'

services:
  # ========== Frontend ==========
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://nginx/api
    depends_on:
      - nginx
    networks:
      - app-network

  # ========== API Gateway ==========
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - auth-service
      - chat-service
      - rag-service
      - whisper-service
    networks:
      - app-network

  # ========== Auth Service ==========
  auth-service:
    build:
      context: ./backend/auth-service
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/streamagent
      - REDIS_URL=redis://redis:6379/0
      - JWT_SECRET=${JWT_SECRET}
      - JWT_ALGORITHM=HS256
      - ACCESS_TOKEN_EXPIRE_MINUTES=60
      - REFRESH_TOKEN_EXPIRE_DAYS=7
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - app-network

  # ========== Chat Service ==========
  chat-service:
    build:
      context: ./backend/chat-service
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/streamagent
      - REDIS_URL=redis://redis:6379/0
      - MILVUS_HOST=milvus
      - MILVUS_PORT=19530
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - E2B_API_KEY=${E2B_API_KEY}
      - BRIGHT_DATA_API_KEY=${BRIGHT_DATA_API_KEY}
    depends_on:
      - postgres
      - redis
      - milvus
    networks:
      - app-network

  # ========== RAG Service ==========
  rag-service:
    build:
      context: ./backend/rag-service
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/streamagent
      - MILVUS_HOST=milvus
      - MILVUS_PORT=19530
      - MINIO_ENDPOINT=minio:9000
      - MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY}
      - MINIO_SECRET_KEY=${MINIO_SECRET_KEY}
      - MINERU_API_KEY=${MINERU_API_KEY}
    depends_on:
      - postgres
      - milvus
      - minio
    networks:
      - app-network

  # ========== Whisper Service ==========
  whisper-service:
    build:
      context: ./backend/whisper-service
      dockerfile: Dockerfile
    environment:
      - WHISPER_MODEL=base
      - DEVICE=cpu
    networks:
      - app-network

  # ========== Databases ==========
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=streamagent
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - app-network

  milvus:
    image: milvusdb/milvus:v2.3.4
    environment:
      - ETCD_ENDPOINTS=etcd:2379
      - MINIO_ADDRESS=minio:9000
    depends_on:
      - etcd
      - minio
    ports:
      - "19530:19530"
    volumes:
      - milvus_data:/var/lib/milvus
    networks:
      - app-network

  etcd:
    image: quay.io/coreos/etcd:v3.5.5
    environment:
      - ETCD_AUTO_COMPACTION_MODE=revision
      - ETCD_AUTO_COMPACTION_RETENTION=1000
      - ETCD_QUOTA_BACKEND_BYTES=4294967296
    volumes:
      - etcd_data:/etcd
    command: etcd -advertise-client-urls=http://127.0.0.1:2379 -listen-client-urls http://0.0.0.0:2379 --data-dir /etcd
    networks:
      - app-network

  minio:
    image: minio/minio:latest
    environment:
      - MINIO_ROOT_USER=${MINIO_ACCESS_KEY}
      - MINIO_ROOT_PASSWORD=${MINIO_SECRET_KEY}
    volumes:
      - minio_data:/data
    command: server /data --console-address ":9001"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3
    networks:
      - app-network

networks:
  app-network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
  milvus_data:
  etcd_data:
  minio_data:
```

### 8.2 Nginx 配置

```nginx
# nginx/nginx.conf

upstream auth_service {
    server auth-service:8001;
}

upstream chat_service {
    server chat-service:8002;
}

upstream rag_service {
    server rag-service:8004;
}

upstream whisper_service {
    server whisper-service:8003;
}

server {
    listen 80;
    server_name localhost;

    # API 路由
    location /api/auth {
        proxy_pass http://auth_service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/chat {
        proxy_pass http://chat_service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        # SSE 支持
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding off;
    }

    location /api/conversations {
        proxy_pass http://chat_service;
        proxy_set_header Host $host;
    }

    location /api/documents {
        proxy_pass http://rag_service;
        proxy_set_header Host $host;
        client_max_body_size 100M;
    }

    location /api/search {
        proxy_pass http://rag_service;
        proxy_set_header Host $host;
    }

    location /api/voice {
        proxy_pass http://whisper_service;
        proxy_set_header Host $host;
        client_max_body_size 50M;
    }

    location /api/settings {
        proxy_pass http://auth_service;
        proxy_set_header Host $host;
    }

    # 健康检查
    location /health {
        return 200 'OK';
        add_header Content-Type text/plain;
    }
}
```

### 8.3 环境变量配置

```bash
# .env

# ========== Database ==========
POSTGRES_PASSWORD=your_secure_password
DATABASE_URL=postgresql://postgres:your_secure_password@postgres:5432/streamagent

# ========== Redis ==========
REDIS_URL=redis://redis:6379/0

# ========== JWT ==========
JWT_SECRET=your_jwt_secret_key_at_least_32_chars
JWT_ALGORITHM=HS256

# ========== MinIO ==========
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# ========== External APIs ==========
GOOGLE_API_KEY=your_google_api_key
E2B_API_KEY=your_e2b_api_key
BRIGHT_DATA_API_KEY=your_bright_data_key
MINERU_API_KEY=your_mineru_api_key

# ========== TTS ==========
EDGE_TTS_VOICE=zh-CN-XiaoxiaoNeural
```

### 8.4 部署流程

```bash
# 1. 克隆项目
git clone <repo_url>
cd My-Chat-LangChain

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 填入必要的 API Key

# 3. 构建并启动所有服务
docker-compose up -d --build

# 4. 查看服务状态
docker-compose ps

# 5. 查看日志
docker-compose logs -f

# 6. 停止服务
docker-compose down

# 7. 清理数据 (谨慎)
docker-compose down -v
```

### 8.5 Render + Supabase 云部署方案 (推荐)

> 适用于快速部署、低运维成本的场景。使用 Supabase 的 pgvector 扩展替代 Milvus。

#### 8.5.1 架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Render + Supabase 云部署架构                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Render (计算层)                         Supabase (数据层)              │
│  ┌─────────────────────┐                ┌─────────────────────────┐    │
│  │ frontend-next       │                │ PostgreSQL + pgvector   │    │
│  │ (Web Service)       │                │                         │    │
│  │ - Next.js 14        │                │ Tables:                 │    │
│  │ - 静态资源          │                │ - users                 │    │
│  └──────────┬──────────┘                │ - conversations         │    │
│             │                           │ - messages              │    │
│  ┌──────────▼──────────┐                │ - documents             │    │
│  │ auth-service        │◄──────────────►│ - document_chunks       │    │
│  │ (Web Service)       │                │   (embedding vector)    │    │
│  │ - 端口 8001         │                │                         │    │
│  └──────────┬──────────┘                └─────────────────────────┘    │
│             │                                                           │
│  ┌──────────▼──────────┐                ┌─────────────────────────┐    │
│  │ chat-service        │                │ Supabase Storage        │    │
│  │ (Web Service)       │                │ (可选)                  │    │
│  │ - 端口 8002         │                │ - PDF/文档存储          │    │
│  │ - LangGraph Agent   │                └─────────────────────────┘    │
│  └──────────┬──────────┘                                               │
│             │                                                           │
│  ┌──────────▼──────────┐                                               │
│  │ rag-service         │                                               │
│  │ (Web Service)       │                                               │
│  │ - 端口 8004         │                                               │
│  │ - pgvector 检索     │                                               │
│  │ - BM25 混合检索     │                                               │
│  └──────────┬──────────┘                                               │
│             │                                                           │
│  ┌──────────▼──────────┐                                               │
│  │ whisper-service     │  (可选: 或使用 OpenAI Whisper API)            │
│  │ (Web Service)       │                                               │
│  │ - 端口 8003         │                                               │
│  └─────────────────────┘                                               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 8.5.2 服务配置

| 服务 | Render 类型 | 配置建议 | 环境变量 |
|------|------------|---------|---------|
| **frontend-next** | Web Service | Starter ($7/月) 或 Free | `NEXT_PUBLIC_API_URL` |
| **auth-service** | Web Service | Starter | `DATABASE_URL`, `JWT_SECRET` |
| **chat-service** | Web Service | Standard ($25/月) | `DATABASE_URL`, `GOOGLE_API_KEY`, `E2B_API_KEY` |
| **rag-service** | Web Service | Standard | `DATABASE_URL`, `EMBEDDING_MODEL` |
| **whisper-service** | Web Service | Standard (需要内存) | `WHISPER_MODEL` |

#### 8.5.3 Supabase 配置

**1. 启用 pgvector 扩展**

```sql
-- 在 Supabase SQL Editor 中执行
CREATE EXTENSION IF NOT EXISTS vector;
```

**2. 创建向量表**

```sql
-- document_chunks 表 (替代 Milvus)
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    page_number INTEGER,
    section VARCHAR(255),
    embedding vector(384),  -- all-MiniLM-L6-v2 维度
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建向量索引 (IVFFlat)
CREATE INDEX ON document_chunks
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- 创建用户隔离索引
CREATE INDEX idx_chunks_user_id ON document_chunks(user_id);
CREATE INDEX idx_chunks_document_id ON document_chunks(document_id);
```

**3. 向量搜索函数**

```sql
-- 相似度搜索函数
CREATE OR REPLACE FUNCTION search_documents(
    query_embedding vector(384),
    match_user_id UUID,
    match_count INT DEFAULT 10
)
RETURNS TABLE (
    id UUID,
    document_id UUID,
    content TEXT,
    page_number INTEGER,
    section VARCHAR,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        dc.id,
        dc.document_id,
        dc.content,
        dc.page_number,
        dc.section,
        1 - (dc.embedding <=> query_embedding) AS similarity
    FROM document_chunks dc
    WHERE dc.user_id = match_user_id
    ORDER BY dc.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
```

#### 8.5.4 rag-service 改造

需要新增 `PgvectorService` 替代 `MilvusService`:

```python
# app/services/pgvector_service.py

from typing import List, Optional
import numpy as np
from sqlalchemy import text
from sqlalchemy.orm import Session

class PgvectorService:
    """
    使用 Supabase pgvector 的向量检索服务
    """

    def __init__(self, db: Session):
        self.db = db

    async def insert(self, chunks: List[ChunkData]) -> None:
        """插入向量数据"""
        for chunk in chunks:
            embedding_str = f"[{','.join(map(str, chunk.embedding))}]"
            self.db.execute(text("""
                INSERT INTO document_chunks
                (id, document_id, user_id, chunk_index, content, page_number, section, embedding, metadata)
                VALUES (:id, :doc_id, :user_id, :idx, :content, :page, :section, :embedding::vector, :meta)
            """), {
                "id": chunk.id,
                "doc_id": chunk.document_id,
                "user_id": chunk.user_id,
                "idx": chunk.chunk_index,
                "content": chunk.content,
                "page": chunk.page_number,
                "section": chunk.section,
                "embedding": embedding_str,
                "meta": chunk.metadata
            })
        self.db.commit()

    async def search(
        self,
        query_embedding: List[float],
        user_id: str,
        top_k: int = 10
    ) -> List[dict]:
        """向量相似度搜索"""
        embedding_str = f"[{','.join(map(str, query_embedding))}]"
        result = self.db.execute(text("""
            SELECT id, document_id, content, page_number, section,
                   1 - (embedding <=> :embedding::vector) AS similarity
            FROM document_chunks
            WHERE user_id = :user_id
            ORDER BY embedding <=> :embedding::vector
            LIMIT :top_k
        """), {
            "embedding": embedding_str,
            "user_id": user_id,
            "top_k": top_k
        })
        return [dict(row) for row in result]

    async def delete_by_document(self, document_id: str) -> None:
        """删除文档的所有向量"""
        self.db.execute(text(
            "DELETE FROM document_chunks WHERE document_id = :doc_id"
        ), {"doc_id": document_id})
        self.db.commit()
```

#### 8.5.5 环境变量配置

```bash
# Render 环境变量

# ========== Supabase ==========
DATABASE_URL=postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
SUPABASE_URL=https://[project-ref].supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key

# ========== JWT ==========
JWT_SECRET=your_jwt_secret_at_least_32_chars
JWT_ALGORITHM=HS256

# ========== External APIs ==========
GOOGLE_API_KEY=your_google_api_key
E2B_API_KEY=your_e2b_api_key
BRIGHT_DATA_API_KEY=your_bright_data_key

# ========== Embedding ==========
EMBEDDING_MODEL=all-MiniLM-L6-v2

# ========== TTS ==========
EDGE_TTS_VOICE=zh-CN-XiaoxiaoNeural
```

#### 8.5.6 部署步骤

```bash
# 1. 创建 Supabase 项目
#    - 访问 https://supabase.com
#    - 创建新项目，记录连接字符串

# 2. 初始化数据库
#    - 在 Supabase SQL Editor 执行上述 SQL
#    - 启用 pgvector 扩展
#    - 创建表和索引

# 3. 在 Render 创建服务
#    - 连接 GitHub 仓库
#    - 为每个微服务创建 Web Service
#    - 配置环境变量

# 4. 配置服务间通信
#    - 使用 Render Private Services 或环境变量配置内部 URL

# 5. 配置前端
#    - NEXT_PUBLIC_API_URL 指向后端服务 URL
```

#### 8.5.7 成本估算

| 服务 | 免费额度 | 付费价格 |
|------|---------|---------|
| **Supabase** | 500MB 数据库, 1GB 存储 | $25/月 (Pro) |
| **Render** (5个服务) | 750小时/月 (会休眠) | ~$50-100/月 |
| **总计** | 可免费试用 | ~$75-125/月 |

#### 8.5.8 pgvector vs Milvus 对比

| 特性 | pgvector (Supabase) | Milvus |
|------|---------------------|--------|
| **部署复杂度** | 低 (内置) | 高 (独立服务) |
| **运维成本** | 低 | 高 |
| **向量维度** | ≤2000 | 更高 |
| **数据规模** | 百万级 | 亿级 |
| **混合查询** | ✅ SQL + 向量 | 需额外处理 |
| **适用场景** | 中小规模 | 大规模 |

> **结论**: 对于个人/小团队知识库项目，pgvector 完全够用，且大幅简化部署架构。

---

## 九、开发计划

### 9.1 阶段划分

```
Phase 1: 前端重构 + 用户系统 (2-3 周)
├── Week 1: Next.js 项目搭建 + 基础 UI
├── Week 2: 用户认证系统 + 会话管理
└── Week 3: 流式聊天集成 + 工具可视化

Phase 2: 多模态能力 (1-2 周)
├── Week 4: 图片上传与理解
└── Week 5: 语音输入/输出

Phase 3: RAG 增强 (2 周)
├── Week 6: Milvus 迁移 + 混合检索
└── Week 7: MinerU 集成 + 引用追溯

Phase 4: 部署优化 (1 周)
└── Week 8: Docker Compose + 测试 + 文档

Phase 5: 扩展功能 (待定)
└── Week 9+: AI 生成 PPT / 文档生成
```

### 9.2 里程碑

| 里程碑 | 完成条件 | 预计日期 |
|--------|---------|---------|
| **M1: 前端可用** | Next.js 前端能正常聊天 | Week 2 |
| **M2: 用户系统** | 注册/登录/会话管理完成 | Week 3 |
| **M3: 多模态** | 图片+语音功能可用 | Week 5 |
| **M4: RAG 增强** | 混合检索+引用追溯完成 | Week 7 |
| **M5: 生产就绪** | Docker Compose 部署完成 | Week 8 |
| **M6: 扩展功能** | AI 生成 PPT 功能可用 | Week 9+ |

### 9.3 详细任务清单

#### Phase 1: 前端重构 + 用户系统

**Week 1: 基础搭建** ✅ 已完成 (2025-12-31)

- [x] 创建 Next.js 14 项目 (实际使用 Next.js 16.1.1)
- [x] 配置 Tailwind CSS + shadcn/ui (Tailwind 4.0)
- [x] 实现基础布局 (Header + Sidebar + Main)
- [x] 创建登录/注册页面 UI
- [x] 创建聊天页面 UI
- [x] 实现消息列表组件
- [x] 实现输入区域组件 (支持图片上传/粘贴/拖拽)
- [x] 配置 Zustand 状态管理 (authStore, chatStore, settingsStore)
- [x] 实现 ThemeProvider (亮色/暗色/系统主题)
- [x] 实现 AuthProvider (路由保护)
- [x] 配置 API 客户端 (Axios + Token 拦截器)
- [x] 创建设置页面 UI

**Week 2: 用户认证** ✅ 已完成 (2025-12-31)

- [x] 创建 auth-service 项目结构
- [x] 实现用户注册 API (POST /api/auth/register)
- [x] 实现用户登录 API (POST /api/auth/login)
- [x] 实现 JWT Token 生成/验证 (bcrypt + python-jose)
- [x] 实现 Refresh Token 机制 (POST /api/auth/refresh)
- [x] 实现用户登出 API (POST /api/auth/logout)
- [x] 实现获取当前用户 API (GET /api/auth/me)
- [x] 前端认证状态管理 (已在 Week 1 完成)
- [x] 前端路由保护 (已在 Week 1 完成)
- [x] API 请求拦截器 (Token 自动携带/刷新) (已在 Week 1 完成)

**Week 3: 聊天集成** ✅ 已完成 (2025-12-31)

- [x] 创建 chat-service 微服务项目结构
- [x] 实现会话 (Conversation) 数据模型
- [x] 实现消息 (Message) 数据模型
- [x] 实现会话 CRUD API (GET/POST/PUT/DELETE)
- [x] 实现消息存储和查询 API
- [x] 实现流式聊天 API (POST /api/chat/stream)
- [x] 集成 LangGraph Agent 服务
- [x] 用户隔离机制 (基于 JWT user_id)
- [x] auth-service JWT Token 增加 username/email 字段
- [x] 前端认证 API 联调 (登录/注册/登出)
- [x] 修复 .gitignore 规则 (恢复 frontend-next/src/lib/ 追踪)
- [x] 前端 SSE 流式处理对接 (chat.ts, chatStore.ts)
- [x] 工具调用可视化组件 (ToolCallPanel.tsx)
- [x] 代码块高亮组件 (CodeBlock.tsx)
- [x] 图表渲染组件 (ImageRenderer.tsx)
- [x] 消息复制/重新生成功能 (MessageBubble.tsx)
- [x] 修复工具导入路径 (agent_service.py)
- [x] 修复前端 UTF-8 中文显示乱码 (decodeBase64UTF8)
- [x] 支持 OpenAI 兼容模式 LLM 配置 (.env.example 更新)

#### Phase 2: 多模态能力

**Week 4: 图片理解** ✅ 已完成 (2026-01-01)

- [x] 前端图片上传组件 (已在 Week 1 完成)
- [x] 图片拖拽/粘贴支持 (已在 Week 1 完成)
- [x] 图片预览与删除 (已在 Week 1 完成)
- [x] 后端多模态消息构建 (build_multimodal_content 函数)
- [x] Vision API 集成 (支持 OpenAI 兼容模式)
- [x] 更新 .env.example 添加视觉模型说明
- [x] 修复 E2B 图表显示问题 (变量名 `images` 冲突改为 `image_matches`)
- [x] 修复 ToolCallPanel 自动展示图片 (无需手动展开)
- [x] 修复 Markdown 图片渲染 (MessageBubble 添加 img 组件)
- [ ] OCR 功能实现 (延后到 Week 5)

**Week 5: 语音交互** ✅ 已完成 (2026-01-01)

- [x] 创建 whisper-service 项目结构
- [x] 集成 faster-whisper 语音识别
- [x] 集成 edge-tts 语音合成
- [x] 前端录音组件 VoiceRecorder (MediaRecorder API)
- [x] 前端音频播放器组件 AudioPlayer
- [x] 语音转文字完整流程 (InputArea 集成)
- [x] 文字转语音完整流程 (MessageBubble 集成)
- [x] 语音设置选项 (Settings 页面 TTS 语音选择)
- [x] 修复路由前缀问题 (/api/v1/voice/*)
- [x] 修复 MIME 类型验证 (支持 codecs 参数)
- [x] 修复 Whisper 转录 (bytes → BytesIO)
- [x] 修复 Edge TTS 合成 (使用 stream_sync())

**Week 5.5: 前端优化** ✅ 已完成 (2026-01-02)

- [x] 新增 ConversationItem 组件 (支持对话重命名和删除)
- [x] 使用 CSS Grid 布局解决长标题挤压按钮的问题
- [x] 修复默认页面重定向逻辑 (未登录跳转 login，已登录跳转 chat)
- [x] 添加 authStore 的 isInitialized 状态用于初始化检测

#### Phase 3: RAG 增强

**Week 6: 向量存储迁移** ✅ 已完成 (2026-01-02)

- [x] 创建 rag-service 项目结构
- [x] Milvus Collection 设计 (milvus_service.py)
- [x] 向量存储服务封装 (MilvusService)
- [x] Embedding 服务封装 (EmbeddingService - sentence-transformers)
- [x] BM25 索引构建 (BM25Service - jieba 中文分词)
- [x] RRF 融合算法实现 (HybridSearchService)
- [x] 混合检索 API (向量+BM25+RRF融合)
- [x] 文档管理 API (CRUD)
- [x] 文档摄取 API (上传/分块/向量化)
- [x] PDF 文本提取 (PyPDF2)
- [x] SQLite 测试模式兼容性修复
- [x] 测试通过: 健康检查、文档上传(71分块)、BM25中文搜索
- [ ] ChromaDB 数据迁移脚本 (待定)

**Week 7: 高级检索**

- [x] Reranker 模型集成 (bge-reranker + 简单关键词重排序)
- [x] 引用追溯实现 (CitationService + 上下文获取)
- [x] 混合搜索 Milvus 空指针修复
- [x] 智能分块服务 (ChunkingService - 语义/页面感知/递归分块)
- [x] 前端引用展示组件 (CitationPanel + RAG API)
- [x] 文档管理界面 (DocumentsPage - 上传/列表/搜索/删除)
- [x] RAG 与 Chat 集成 (rag_search + list_knowledge_documents 工具)
- [x] RAG 检索优化 (chunk_size: 500→1500, overlap: 50→200, top_k: 5→10)
- [x] LLM RAG 结果利用优化 (System Prompt 增加 RAG 使用指南 + 工具输出格式优化)
- [x] 引用展示优化 - 结构化引用数据传递 ([RAG_CITATIONS] 标记 + citation SSE 事件)
- [x] 引用展示优化 - 完整内容弹窗 (CitationPanel 展开详情 + 前后文上下文)
- [x] 文档目录提取功能 (extract_toc + chunk_with_toc - 提升长篇书籍章节问答准确性)
- [x] 前端文档列表 UI 修复 (CSS Grid 布局解决长文件名挤压问题)
- [ ] 引用展示优化 - 引用高亮标记 (待定)
- [ ] MinerU API 集成 (可选)
- [ ] 多轮对话检索优化

#### Phase 4: 部署优化

**Week 8: 部署与测试**

> 部署方案: Render (计算) + Supabase (数据库 + pgvector 向量存储)

- [x] PgvectorService 实现 (替代 MilvusService) ✅ 2026-01-03
- [x] rag-service 适配 pgvector (API 层兼容) ✅ 2026-01-03
- [x] PgvectorService 自动化测试 (11 项测试全通过) ✅ 2026-01-03
- [x] Supabase 数据库 Schema 设计与迁移 ✅ 2026-01-03
- [x] Render 部署配置 (render.yaml) ✅ 2026-01-03
- [x] 服务健康检查实现 (已内置 /health 端点) ✅ 2026-01-03
- [x] 环境变量管理 (.env.example 更新) ✅ 2026-01-03
- [x] 部署文档编写 (docs/deploy-render.md) ✅ 2026-01-03
- [x] 前端构建与部署配置 (Dockerfile + next.config.ts + API客户端优化) ✅ 2026-01-03
- [x] 端到端测试脚本 (tests/test_e2e.py + health_check.py) ✅ 2026-01-03

**备选: Docker Compose 本地部署**
- [ ] 完善 Docker Compose 配置
- [ ] Nginx 反向代理配置
- [ ] 本地 Milvus 配置

#### Phase 5: AI 生成 PPT 完整方案 (独立服务架构)

> **架构决策**: 采用方案 B - 完整独立的 presentation-service
>
> **设计目标**: 打造精美实用、图文并茂、可自定义模板和风格、具备迭代优化功能的 AI 演示文稿生成系统

---

#### 5.1 整体架构设计

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js 14)                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  /presentations/                    # 演示文稿独立页面                       │
│  ├── page.tsx                       # 列表页 + 快速创建                      │
│  ├── [id]/page.tsx                  # 编辑器 + 预览页                        │
│  ├── new/page.tsx                   # 创建配置页                             │
│  └── components/                                                           │
│      ├── PresentationCard.tsx      # 文稿卡片                               │
│      ├── PresentationEditor.tsx     # 主编辑器组件                          │
│      ├── SlideThumbnail.tsx        # 幻灯片缩略图                           │
│      ├── PresentationConfigPanel.tsx # 配置面板                             │
│      └── PresentationPreview.tsx   # 预览组件 (复用)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  /lib/stores/presentationStore.ts   # Zustand 状态管理                      │
│  /lib/api/presentation.ts           # API 客户端                            │
│  /lib/types/presentation.ts         # TypeScript 类型定义                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                            HTTP/REST + SSE
                                    │
┌─────────────────────────────────────────────────────────────────────────────┐
│                   presentation-service (FastAPI)                             │
│  Port: 8005                                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│  ├── app/                                                                  │
│  │   ├── main.py                        # FastAPI 入口                     │
│  │   ├── config.py                      # 配置管理                          │
│  │   ├── models/                        # SQLAlchemy 模型                   │
│  │   │   ├── presentation.py           # 演示文稿模型                      │
│  │   │   └── slide_version.py           # 幻灯片版本模型 (可选)             │
│  │   ├── schemas/                       # Pydantic Schema                   │
│  │   │   ├── presentation.py            # 请求/响应 Schema                   │
│  │   │   └── slide.py                   # 幻灯片 Schema                     │
│  │   ├── api/v1/                        # API 路由                          │
│  │   │   ├── presentations.py           # CRUD API                         │
│  │   │   └── editor.py                  # 编辑器 API (换主题/重生成)         │
│  │   └── services/                      # 业务逻辑                          │
│  │       ├── presentation_service.py   # 演示文稿服务                      │
│  │       ├── layout_engine.py          # 布局引擎                          │
│  │       ├── image_service.py          # 图片服务 (Unsplash)                │
│  │       └── theme_service.py          # 主题服务                          │
│  └── requirements.txt                                                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                            ┌───────┴───────┐
                            ▼               ▼
┌─────────────────────┐  ┌─────────────────────────────────────────────────┐
│  PostgreSQL         │  │  External Services                             │
│  - presentations    │  │  - Unsplash API (图片)                         │
│  - slide_versions   │  │  - Pexels API (备选)                           │
│  - user_settings    │  │  - E2B Sandbox (代码执行/图表)                 │
└─────────────────────┘  └─────────────────────────────────────────────────┘
```

---

#### 5.2 导航结构设计

```
登录后
    │
    ├── 📝 对话 chat/               ← AI 对话 (可快速生成 PPT)
    ├── 🎊 演示文稿 presentations/  ← 新增：PPT 独立页面
    ├── 📚 文档管理 documents/      ← RAG 文档管理
    └── ⚙️ 设置 settings/
```

#### 5.3 数据库设计

```sql
-- 演示文稿表
CREATE TABLE presentations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,

    -- 核心内容
    slides JSONB NOT NULL,              -- 幻灯片数组
    layout_config JSONB DEFAULT '{}',   -- 布局配置

    -- 样式配置
    theme VARCHAR(50) DEFAULT 'modern_business',
    custom_theme JSONB,                 -- 自定义主题配置

    -- 生成配置
    target_audience VARCHAR(100),
    presentation_type VARCHAR(50),      -- informative, persuasive, instructional
    include_images BOOLEAN DEFAULT true,
    image_style VARCHAR(50),

    -- 元数据
    slide_count INTEGER DEFAULT 0,
    thumbnail TEXT,                     -- 预览图 URL (Base64)

    -- 状态
    status VARCHAR(20) DEFAULT 'draft', -- draft, completed, archived

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 幻灯片版本表 (可选，用于版本管理和回滚)
CREATE TABLE slide_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    presentation_id UUID REFERENCES presentations(id) ON DELETE CASCADE,
    slide_index INTEGER NOT NULL,
    content JSONB NOT NULL,
    layout VARCHAR(50),
    version_number INTEGER DEFAULT 1,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_presentations_user_id ON presentations(user_id);
CREATE INDEX idx_presentations_status ON presentations(status);
CREATE INDEX idx_presentations_created_at ON presentations(created_at DESC);
CREATE INDEX idx_slide_versions_presentation ON slide_versions(presentation_id);
```

---

#### 5.4 API 接口设计

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| **基础 CRUD** |
| POST | /api/presentations | 创建新演示文稿 | 是 |
| GET | /api/presentations | 获取用户文稿列表 | 是 |
| GET | /api/presentations/{id} | 获取文稿详情 | 是 |
| PUT | /api/presentations/{id} | 更新文稿 | 是 |
| DELETE | /api/presentations/{id} | 删除文稿 | 是 |
| **AI 生成** |
| POST | /api/presentations/generate | AI 生成演示文稿 | 是 |
| POST | /api/presentations/{id}/regenerate/{slide_index} | 重新生成指定幻灯片 | 是 |
| **编辑功能** |
| POST | /api/presentations/{id}/theme | 更换主题 | 是 |
| POST | /api/presentations/{id}/layout/{slide_index} | 更改布局 | 是 |
| POST | /api/presentations/{id}/slides | 添加幻灯片 | 是 |
| DELETE | /api/presentations/{id}/slides/{slide_index} | 删除幻灯片 | 是 |
| PUT | /api/presentations/{id}/slides/{slide_index} | 更新幻灯片内容 | 是 |
| **导入导出** |
| GET | /api/presentations/{id}/export/html | 导出 HTML | 是 |
| GET | /api/presentations/{id}/export/pdf | 导出 PDF (可选) | 是 |

---

#### 5.5 开发阶段规划

**Phase 5.1: Reveal.js 网页演示 (基础版)** ✅ 已完成 (2026-01-03)
- [x] 新增 `generate_presentation` 工具 (在 chat-service)
- [x] 支持基础幻灯片结构 (标题、内容、图片)
- [x] 前端 PPT 预览组件 (iframe 嵌入)
- [x] 主题选择 (black, white, league 等 9种主题)

**Phase 5.2: 独立服务基础设施** ✅ 已完成 (2026-01-03)
- [x] 创建 presentation-service 项目结构
- [x] 实现数据模型 (Presentation, SlideVersion)
- [x] 实现 CRUD API (presentations.py)
- [x] 实现编辑器 API (editor.py - 换主题/重生成/增删幻灯片)
- [x] 实现服务层 (PresentationService - AI生成幻灯片)
- [x] 支持 OpenAI 兼容模式 LLM (ChatOpenAI 集成)
- [x] 健康检查端点 (/health)
- [x] SQLite UUID 兼容性修复
- [x] Token 验证超时优化 (5s → 10s)

**Phase 5.3: 前端独立页面** ✅ 已完成 (2026-01-03)
- [x] 创建 `/presentations` 路由和页面
- [x] 创建 `/presentations/[id]` 编辑器页面
- [x] 实现 presentationStore 状态管理
- [x] 实现 API 客户端 (presentations.ts)
- [x] 创建演示文稿列表页 (PresentationListPage)
- [x] 创建演示文稿编辑器页面 (PresentationEditorPage)
- [x] 创建幻灯片缩略图组件
- [x] 创建幻灯片编辑器组件 (SlideEditor - 标题/内容/布局/备注)
- [x] 创建幻灯片预览组件 (SlidePreview)
- [x] 创建主题选择器 (ThemeSelector)
- [x] 创建演示文稿播放器 (PresentationPlayer)
- [x] 创建对话框组件 (Dialog - 用于创建/换主题/重新生成)
- [x] 缺失组件补齐 (Select - Radix UI)

**Phase 5.4: 在线编辑器功能** ✅ 已完成并测试通过 (2026-01-04)
- [x] 幻灯片文本内容实时编辑 (标题/内容/备注) ✅ 测试通过
- [x] 插入新幻灯片功能 (支持在任意位置插入) ✅ 测试通过
- [x] 删除幻灯片功能 ✅ 测试通过
- [x] 编辑状态自动保存 (1秒防抖) ✅ 测试通过
- [x] 布局类型切换 (7种布局) ✅ 测试通过
- [x] 数据持久化 (刷新后保留) ✅ 测试通过
- [ ] 幻灯片拖拽排序 (待后续实现)
- [ ] 撤销/重做操作 (待后续实现)

**Phase 5.5: AI 对话式修改** ✅ 基础功能已完成 (2026-01-04)
- [x] AI 助手对话面板 (右侧边栏 - AssistantPanel.tsx)
- [x] 自然语言指令解析 (IntentParserService - 支持10种意图类型)
- [x] AI 助手后端 API (assistant.py - POST /assistant/{id}/chat)
- [x] 前端集成到编辑器页面 (AI 助手按钮 + 右侧面板)
- [x] 自动化测试 (14项测试全通过)
- [ ] 多轮对话上下文优化 (待后续完善)
- [ ] AI 自动调整布局和风格 (待后续完善)
- [ ] 修改历史记录和回滚 (待后续完善)

**Phase 5.7: 高级生成功能** ✅ 已完成 (2026-01-06)
- [x] 智能布局引擎 (19 种布局类型) ✅ 42项测试通过
- [x] 图片集成 (Unsplash API + 备用方案) ✅ 31项测试通过
- [x] 高级主题系统 (12 种精品主题) ✅ 40项测试通过
- [ ] Markdown 高级语法支持 (待后续)

**Phase 5.8: 导出与协作** ✅ 已完成 (2026-01-07)
- [x] 导出 HTML (含 Reveal.js / 简洁版) ✅ 34项测试通过
- [x] 前端导出按钮集成 ✅
- [x] 浏览器预览功能 ✅
- [ ] 导出 PDF (可选)
- [ ] 从聊天快速跳转 (可选)
- [ ] 分享链接 (可选)

**Phase 5.9: 美学优化与 Bug 修复** ✅ 已完成

> 基于用户测试反馈，发现以下问题需要修复和优化

**5.9.1 Bug 修复 (高优先级)** ✅ 已完成

- [x] HTML 结构错误：列表标签不完整 (缺少 `<ul>` 开始标签) ✅ commit 9abe270
- [x] Markdown 换行符解析：`\n` 被当作文本输出而非换行 ✅ commit 9abe270
- [x] 布局内容缺失：两栏/三栏布局右侧内容为占位符 ✅ commit b1f6662
- [x] 封面页标题层级：应使用 `<h1>` 而非 `<h2>` ✅ commit 9abe270

**5.9.2 主题系统增强** ✅ 已完成 (commit b1f6662)

当前问题：用户指定"二次元风格"但系统使用默认商务主题

新增主题：
| 主题 ID | 名称 | 适用场景 | 配色方案 |
|---------|------|----------|----------|
| anime_dark | 二次元暗黑 | 动漫/游戏介绍 | 深色背景 + 霓虹色 |
| anime_cute | 二次元可爱 | 萌系/日常番 | 粉彩色系 |
| cyberpunk | 赛博朋克 | 科幻/机甲番 | 紫色/青色/粉色 |
| eva_nerv | EVA NERV | 新世纪福音战士专用 | 紫/绿/橙/黑红 |
| retro_pixel | 复古像素 | 游戏/怀旧 | 8-bit 色彩 |

EVA 专用配色方案：
```css
:root {
    --eva-purple: #5B2C6F;      /* 初号机紫 */
    --eva-green: #1ABC9C;       /* 初号机绿 */
    --eva-orange: #E74C3C;      /* 贰号机橙红 */
    --eva-blue: #3498DB;        /* 零号机蓝 */
    --nerv-red: #C0392B;        /* NERV 红 */
    --nerv-black: #1C1C1C;      /* 背景黑 */
    --terminal-green: #00FF00;  /* 终端绿 */
}
```

**5.9.3 图片服务集成** ✅ 已完成 (commit 03c9a61)

当前问题：AI 生成时未调用图片服务，导致"图文并茂"需求无法满足

改进方案：
1. [x] AI 生成流程中自动调用 ImageService
2. [x] 根据幻灯片内容智能推荐图片关键词
3. [x] 支持用户指定图片风格 (写实/插画/二次元)
4. [x] 图片布局自动适配 (全屏/半屏/缩略图)

**5.9.4 智能主题匹配** ✅ 已完成 (commit b1f6662)

根据用户输入自动推荐主题：
| 关键词 | 推荐主题 |
|--------|----------|
| 动漫/二次元/番剧 | anime_dark / anime_cute |
| 商务/企业/报告 | modern_business / corporate_blue |
| 科技/AI/编程 | dark_tech / neon_future |
| 学术/论文/研究 | academic_classic / minimal_white |
| 游戏/电竞 | cyberpunk / retro_pixel |

**5.9.5 视觉效果增强**

- [ ] 添加幻灯片切换动画选项
- [ ] 支持背景图片/渐变
- [ ] 添加装饰元素 (几何图形/线条)
- [ ] 代码块语法高亮优化

---

#### 5.6 在线编辑器设计

##### 5.6.1 实时编辑功能

**前端组件架构:**
```typescript
// components/presentation/SlideEditor.tsx

interface SlideEditorProps {
  slideIndex: number;
  slide: Slide;
  onUpdate: (index: number, updates: Partial<Slide>) => void;
  readOnly?: boolean;
}

// 功能:
// 1. 标题编辑 (ContentEditable + 自动保存)
// 2. 内容编辑 (支持 Markdown 预览)
// 3. 备注编辑 (演讲者备注)
// 4. 布局选择
// 5. 背景颜色/图片设置
```

**自动保存机制:**
```typescript
// 使用 debounce 防抖
const autoSave = useDebouncedCallback(
  async (updates: Partial<Slide>) => {
    await updateSlide(presentationId, slideIndex, updates);
  },
  1000 // 1秒后自动保存
);
```

##### 5.6.2 插入/删除幻灯片

**插入操作:**
- 点击"添加幻灯片"按钮
- 选择插入位置（当前页之后/末尾）
- 选择幻灯片布局模板
- 创建新幻灯片并刷新列表

**删除操作:**
- 至少保留一张幻灯片
- 删除前确认对话框
- 删除后自动选中下一张

---

#### 5.7 AI 对话式修改设计

##### 5.7.1 整体架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                        PPT 编辑器界面                                 │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────┐ │
│  │   幻灯片缩略图列表   │  │    主编辑区域       │  │  AI 助手    │ │
│  │   (左侧)            │  │    (中间)           │  │  (右侧)     │ │
│  │                     │  │                     │  │             │ │
│  │ ┌───┐ ┌───┐ ┌───┐  │  │  ┌───────────────┐ │  │ ┌─────────┐ │ │
│  │ │ 1 │ │ 2 │ │ 3 │  │  │  │  标题编辑框    │ │  │ │ 对话历史│ │ │
│  │ └───┘ └───┘ └───┘  │  │  ├───────────────┤ │  │ │         │ │ │
│  │                     │  │  │  内容编辑框    │ │  │ │ 用户:   │ │ │
│  │ [+ 添加幻灯片]      │  │  │               │ │  │ │ "帮我把  │ │ │
│  │                     │  │  │               │ │  │ │  第3页   │ │ │
│  │                     │  │  └───────────────┘ │  │ │  标题改  │ │ │
│  │                     │  │                     │  │ │  成..." │ │ │
│  │                     │  │  [预览] [播放]      │  │ │         │ │ │
│  └─────────────────────┘  └─────────────────────┘  │ │ AI:      │ │ │
│                                                  │ │ │ 好的,我  │ │ │
│                                                  │ │ │ 已将第3  │ │ │
│                                                  │ │ │ 页的标题 │ │ │
│                                                  │ │ │ 修改完成 │ │ │
│                                                  │ └─────────┘ │ │
│                                                  │ ┌─────────┐ │ │
│                                                  │ │ 输入框  │ │ │
│                                                  │ └─────────┘ │ │
│                                                  └─────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

##### 5.7.2 自然语言指令解析

**支持的指令类型:**

| 指令类型 | 示例 | API 调用 |
|---------|------|---------|
| 修改标题 | "把第3页的标题改成xxx" | `PUT /slides/{2}` |
| 修改内容 | "在第5页添加一段关于xxx的内容" | `PUT /slides/{4}` |
| 插入幻灯片 | "在第2页后插入一张关于xxx的幻灯片" | `POST /slides` |
| 删除幻灯片 | "删除第4页" | `DELETE /slides/{3}` |
| 调整布局 | "把第1页改成双栏布局" | `PUT /slides/{0}` + layout |
| 更换主题 | "把整个PPT换成深色主题" | `POST /theme` |
| 重新生成 | "重新生成第3页" | `POST /regenerate/{2}` |

##### 5.7.3 AI 助手实现

**后端 API 设计:**
```python
# app/api/v1/assistant.py

@router.post("/chat")
async def assistant_chat(
    presentation_id: str,
    message: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    AI 助手对话接口
    解析自然语言指令并执行相应操作
    """
    # 1. 获取演示文稿
    presentation = await get_presentation(db, presentation_id, user_id)

    # 2. 解析用户意图
    intent = await parse_user_intent(message, presentation)

    # 3. 执行操作
    result = await execute_intent(db, presentation, intent)

    # 4. 返回结果
    return {
        "response": intent.response_message,
        "presentation": result,
        "actions": intent.actions_performed
    }
```

**意图解析 Prompt:**
```python
INTENT_ANALYSIS_SYSTEM_PROMPT = """
你是一个 PPT 编辑助手，负责解析用户的自然语言指令并转换为结构化操作。

当前演示文稿信息:
- 幻灯片数量: {slide_count}
- 当前选中: {current_slide}

请分析用户指令，返回以下 JSON 格式:
{
  "intent_type": "edit_title|edit_content|insert_slide|delete_slide|change_layout|change_theme|regenerate|chat",
  "target_slide": 2,  // 目标幻灯片索引 (从0开始)
  "new_value": "...", // 新值
  "response_message": "确认消息",
  "confidence": 0.95  // 置信度
}

示例:
用户: "把第3页的标题改成人工智能发展史"
输出: {"intent_type": "edit_title", "target_slide": 2, "new_value": "人工智能发展史", ...}

用户: "在当前页后插入一张新幻灯片"
输出: {"intent_type": "insert_slide", "target_slide": {current}, ...}
"""
```

##### 5.7.4 多轮对话上下文

```python
class ConversationContext:
    """对话上下文管理"""

    def __init__(self):
        self.history: List[dict] = []
        self.current_presentation_id: str = None
        self.last_action: str = None

    def add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content})

    def get_context_summary(self) -> str:
        """获取上下文摘要"""
        return f"""
        对话历史摘要:
        - 最后操作: {self.last_action}
        - 对话轮数: {len(self.history) // 2}
        """
```

---

#### 5.8 智能布局系统

**布局类型清单:**
```python
LAYOUT_TYPES = {
    # === 基础布局 ===
    "title_cover": "封面页 - 大标题 + 副标题 + 作者",
    "title_section": "章节页 - 居中大标题",
    "bullet_points": "列表页 - 标题 + 3-6 个要点",
    "two_column": "双栏布局 - 左文右图/双列表",
    "image_text": "图文混排 - 大图配文字说明",

    # === 数据展示 ===
    "chart_single": "单图表 - 标题 + 图表区域",
    "chart_dual": "双图表对比 - 并排两个图表",
    "data_table": "数据表格 - 标题 + 表格 + 说明",
    "metric_card": "指标卡片 - 3-4 个关键指标",

    # === 特殊效果 ===
    "quote_center": "引用页 - 居中引用文字",
    "timeline": "时间线 - 垂直/水平时间轴",
    "process_flow": "流程图 - 步骤流程展示",
    "comparison": "对比布局 - 左右对比两栏",
    "gallery": "图片画廊 - 网格图片展示",

    # === 结尾 ===
    "thank_you": "结尾页 - 感谢 + Q&A",
    "contact": "联系方式 - 社交媒体/邮箱/二维码",
}
```

---

#### 5.9 图片智能集成

**图片来源策略:**
```python
IMAGE_SOURCES = {
    "unsplash": "https://source.unsplash.com/featured/{keyword}",  # 免费
    "pexels": "Pexels API",  # 需要 API Key，免费额度大
    "user_upload": "用户上传的图片",
    "ai_generated": "AI 生成的图表/图片",
}

# 关键词映射
KEYWORD_MAPPING = {
    "科技": ["technology", "innovation", "digital", "futuristic"],
    "商业": ["business", "meeting", "office", "corporate"],
    "自然": ["nature", "landscape", "environment", "outdoor"],
    "人物": ["people", "team", "person", "professional"],
}
```

---

#### 5.10 高级主题系统

**主题预设:**
```python
THEME_PRESETS = {
    "modern_business": {
        "colors": {"primary": "#1e3a8a", "accent": "#3b82f6", "background": "#ffffff"},
        "fonts": {"title": "Montserrat", "body": "Open Sans"},
        "style": "clean, professional, gradient accents",
    },
    "dark_tech": {
        "colors": {"primary": "#00ff88", "accent": "#00d4ff", "background": "#0a0a0a"},
        "fonts": {"title": "Rajdhani", "body": "Roboto Mono"},
        "style": "cyberpunk, neon, grid background",
    },
    "creative_colorful": {
        "colors": {"primary": "#ff6b6b", "accent": "#feca57", "background": "#f8f9fa"},
        "fonts": {"title": "Poppins", "body": "Lato"},
        "style": "vibrant, playful, illustrations",
    },
    "minimal_academic": {
        "colors": {"primary": "#2c3e50", "accent": "#3498db", "background": "#ffffff"},
        "fonts": {"title": "Georgia", "body": "Helvetica"},
        "style": "minimal, serif headers, clean",
    },
    "elegant_dark": {
        "colors": {"primary": "#d4af37", "accent": "#f4e4bc", "background": "#1a1a1a"},
        "fonts": {"title": "Playfair Display", "body": "Lora"},
        "style": "luxury, gold accents, dark",
    },
}
```

---

#### 5.11 完整数据结构

```python
class Slide(BaseModel):
    title: str
    content: str  # 支持 Markdown
    layout: str = "bullet_points"  # 布局类型
    background: Optional[str] = None  # 颜色或图片 URL
    notes: Optional[str] = None  # 演讲者备注
    images: List[SlideImage] = []
    charts: List[ChartConfig] = []
    fragments: List[str] = []  # 逐步显示的片段
    transition: str = "slide"  # 切换动画

class SlideImage(BaseModel):
    url: str
    position: str  # left, right, top, bottom, background
    size: str = "medium"  # small, medium, large, full
    caption: Optional[str] = None

class PresentationConfig(BaseModel):
    topic: str
    theme: str = "modern_business"
    slide_count: int = 10
    target_audience: str = "general"
    presentation_type: str = "informative"  # persuasive, informative, instructional
    include_images: bool = True
    image_style: str = "professional"
```

---

#### 5.12 开发优先级

| 优先级 | 功能 | 说明 |
|--------|------|------|
| **P0** | presentation-service 基础设施 | 项目结构、数据模型、CRUD API |
| **P0** | 数据库迁移 | PostgreSQL 表创建 |
| **P1** | 前端独立页面 | `/presentations` 路由和列表页 |
| **P1** | 编辑器页面 | `/presentations/[id]` 编辑和预览 |
| **P1** | 从聊天跳转 | 聊天生成 PPT 后可跳转到独立页面 |
| **P2** | 高级布局系统 | 15+ 布局类型实现 |
| **P2** | 图片集成 | Unsplash API 集成 |
| **P2** | 高级主题系统 | 5+ 精品主题 |
| **P3** | 迭代优化功能 | 单页重生成、主题切换 |
| **P3** | 导出功能 | HTML/PDF 导出 |

---

##### 5.13 Phase 5.10 美学优化方案 (2026-01-08)

**问题分析 (资深美学设计师视角):**

从当前 PPT 效果截图分析，存在以下美学问题：

###### 1. 图片问题 (严重 - P0)

| 问题 | 描述 | 影响 |
|------|------|------|
| **图片与内容不相关** | EVA 动漫主题显示海边风景照片 | 严重破坏主题一致性 |
| **图片位置不合理** | 图片被挤在右侧角落，与文字割裂 | 视觉重心失衡 |
| **图片尺寸不一致** | 不同幻灯片图片大小位置不统一 | 缺乏专业感 |

**根本原因**: Picsum Photos 是随机图片服务，无法根据内容关键词返回相关图片。

###### 2. 布局问题 (中等 - P1)

| 问题 | 描述 | 影响 |
|------|------|------|
| **封面页布局失衡** | 标题居中但内容靠左，图片靠右 | 视觉重心不稳 |
| **空间利用率低** | 大量空白区域未被有效利用 | 显得空洞 |
| **备注提示干扰** | "演讲者备注可用"出现在演示视图 | 不专业 |

###### 3. 排版问题 (中等 - P1)

| 问题 | 描述 | 影响 |
|------|------|------|
| **标题层级不清晰** | 封面副标题与正文混在一起 | 信息层次混乱 |
| **文字图片间距不协调** | 缺乏呼吸感 | 视觉拥挤 |
| **第三张布局混乱** | 标题、内容、图片、备注挤在一起 | 信息过载 |

---

**改进方案:**

###### 5.13.1 Phase 5.10.1 移除随机图片，优化纯文字布局 (P0)

**策略**: 既然无法获取相关图片，不如移除图片，专注于优化纯文字布局的美学效果。

```python
# 布局优化策略
LAYOUT_IMPROVEMENTS = {
    "title_cover": {
        "改进": "标题居中，副标题下方，移除图片",
        "样式": "大标题 + 渐变背景 + 装饰线条",
    },
    "bullet_points": {
        "改进": "移除右侧图片，内容居中或左对齐",
        "样式": "清晰的列表层级 + 适当间距",
    },
    "image_text": {
        "改进": "改为纯文字双栏布局",
        "样式": "左右分栏 + 视觉平衡",
    },
}
```

**实施步骤:**
- [ ] 修改 SlidePreview 组件，优化无图片时的布局
- [ ] 封面页：标题居中，副标题下方，添加装饰元素
- [ ] 内容页：移除图片占位，内容区域扩展
- [ ] 移除"演讲者备注可用"提示

###### 5.13.2 Phase 5.10.2 增强视觉层次 (P1)

```css
/* 标题层级优化 */
.slide-title-cover h1 { font-size: 3.5rem; font-weight: 700; }
.slide-title-cover .subtitle { font-size: 1.5rem; opacity: 0.8; margin-top: 1rem; }

/* 内容间距优化 */
.slide-content li { margin-bottom: 1rem; line-height: 1.6; }
.slide-content li::marker { color: var(--accent-color); }
```

**实施步骤:**
- [ ] 优化标题字体大小和层级
- [ ] 增加列表项间距
- [ ] 添加装饰性元素（分隔线、图标等）

###### 5.13.3 Phase 5.10.3 未来图片方案 (P2 - 可选)

如果需要真正相关的图片，考虑以下方案：

| 方案 | 优点 | 缺点 |
|------|------|------|
| **Unsplash API** | 可按关键词搜索 | 需要 API Key，有速率限制 |
| **Pexels API** | 免费额度大 | 需要注册 |
| **AI 生成图片** | 完全相关 | 需要 DALL-E/Midjourney API，成本高 |
| **用户上传** | 完全可控 | 需要用户操作 |

**推荐**: 暂时移除图片，专注于纯文字布局的美学优化。未来可添加 Unsplash API 集成。






---

#### 5.14 Phase 5.11 原生 PPTX 导出功能 (2026-01-23)

> **背景**: 参考 pptx-skills 的实现方式，为 presentation-service 添加原生 .pptx 文件导出能力

##### 5.14.1 技术差异分析

| 特性 | pptx-skills | 当前 presentation-service |
|------|-------------|--------------------------|
| **输出格式** | 原生 .pptx 文件 (PptxGenJS) | HTML (Reveal.js) |
| **布局精度** | 像素级精确定位 | CSS 布局 (相对定位) |
| **图片处理** | Sharp 光栅化 + 精确位置 | URL 引用 |
| **主题系统** | 完整配色方案 + 字体 | CSS 变量 |
| **图表支持** | PptxGenJS 原生图表 | 无 |
| **模板支持** | 支持模板复用 | 不支持 |
| **缩略图** | 自动生成预览 | 无 |
| **验证机制** | 视觉验证 + 溢出检测 | 无 |

##### 5.14.2 改进方案

**方案选择**: 使用 Python 原生库 `python-pptx` 实现 PPTX 导出

**理由**:
1. 与现有 Python 后端技术栈一致
2. 无需引入 Node.js 依赖
3. python-pptx 功能成熟，支持完整的 PPTX 操作
4. 可复用现有的主题和布局系统

##### 5.14.3 实现计划

**Phase 5.11.1: PPTX 导出服务 (核心)**

```python
# app/services/pptx_export_service.py
class PptxExportService:
    """原生 PPTX 导出服务"""

    async def export_to_pptx(
        self,
        presentation: Dict[str, Any],
        theme: str = "modern_business"
    ) -> bytes:
        """导出为 PPTX 文件"""
        pass

    def _create_slide(self, prs, slide_data, layout_type):
        """创建单个幻灯片"""
        pass

    def _apply_theme(self, prs, theme_name):
        """应用主题样式"""
        pass
```

**功能清单**:
- [x] 基础 PPTX 生成 (标题页/内容页/结尾页)
- [ ] 19 种布局类型映射到 PPTX 布局
- [ ] 17 种主题配色应用
- [ ] 图片嵌入 (URL 下载 + 嵌入)
- [ ] 表格支持
- [ ] 图表支持 (基础柱状图/饼图)
- [ ] 演讲者备注
- [ ] 自定义字体

**Phase 5.11.2: API 端点**

```python
# app/api/v1/editor.py
@router.get("/{presentation_id}/export/pptx")
async def export_pptx(presentation_id: str):
    """导出为 PPTX 文件"""
    pass
```

**Phase 5.11.3: 前端集成**

- [ ] 导出下拉菜单添加 "下载 PPTX" 选项
- [ ] 导出进度提示 (大文件可能需要时间)

##### 5.14.4 布局映射表

| 系统布局 | PPTX 布局 | 说明 |
|---------|----------|------|
| title_cover | Title Slide | 封面页 |
| title_section | Section Header | 章节页 |
| bullet_points | Title and Content | 列表页 |
| two_column | Two Content | 双栏布局 |
| three_column | 自定义 | 三栏布局 |
| image_full | Blank + 全屏图片 | 全屏图片 |
| image_left | Picture with Caption | 左图右文 |
| image_right | Picture with Caption (镜像) | 右图左文 |
| quote_center | Blank + 居中文本 | 引用页 |
| metric_card | 自定义 | 指标卡片 |
| timeline | 自定义 | 时间线 |
| comparison | Comparison | 对比布局 |
| thank_you | Title Slide | 感谢页 |

##### 5.14.5 主题配色映射

```python
PPTX_THEME_COLORS = {
    "modern_business": {
        "background": "FFFFFF",
        "text": "1E3A8A",
        "accent1": "3B82F6",
        "accent2": "60A5FA",
    },
    "dark_tech": {
        "background": "0A0A0A",
        "text": "00FF88",
        "accent1": "00D4FF",
        "accent2": "FF00FF",
    },
    # ... 其他 15 种主题
}
```

##### 5.14.6 依赖项

```txt
# requirements.txt 新增
python-pptx>=0.6.21
Pillow>=10.0.0  # 图片处理
requests>=2.31.0  # 下载远程图片
```

##### 5.14.7 测试计划

| 测试类型 | 测试内容 | 预期结果 |
|---------|---------|---------|
| 单元测试 | 基础 PPTX 生成 | 生成有效的 .pptx 文件 |
| 单元测试 | 各布局类型 | 19 种布局正确渲染 |
| 单元测试 | 主题应用 | 17 种主题配色正确 |
| 单元测试 | 图片嵌入 | 图片正确显示 |
| 集成测试 | API 端点 | 返回有效的 PPTX 文件 |
| E2E 测试 | 前端下载 | 文件可在 PowerPoint 中打开 |

---

#### 5.15 Phase 5.12 专业级 PPTX 导出升级 (2026-01-23)

> **背景**: 基于 pptx-skills 的深度分析，将当前简陋的 PPTX 导出升级为商用专业级别

##### 5.15.1 当前问题分析

从用户测试反馈来看，当前 PPTX 导出存在以下问题：

| 问题类别 | 具体问题 | 影响程度 |
|---------|---------|---------|
| **排版简陋** | 文字位置固定，缺乏视觉层次 | 高 |
| **字体单一** | 仅使用默认字体，无专业感 | 中 |
| **装饰不足** | 装饰线过于简单，缺乏设计感 | 中 |
| **间距不当** | 列表项间距过小，阅读体验差 | 高 |
| **颜色应用** | 主题色应用不够丰富 | 中 |
| **缺少阴影** | 形状无阴影效果，缺乏立体感 | 低 |

##### 5.15.2 pptx-skills 专业特性分析

从 pptx-skills 的 html2pptx.js 和 SKILL.md 中提取的专业级特性：

**1. 精确定位系统**
```javascript
// pptx-skills 使用精确的单位转换
const PT_PER_PX = 0.75;
const PX_PER_IN = 96;
const EMU_PER_IN = 914400;

// 位置计算精确到英寸
const pxToInch = (px) => px / PX_PER_IN;
```

**2. 专业排版参数**
- 字体大小: 标题 32-44pt, 正文 18-20pt, 副标题 20-24pt
- 行间距: 1.2-1.5 倍行高
- 段落间距: 8-12pt
- 边距: 0.5 英寸标准边距
- 文本框内边距: 精确控制

**3. 视觉设计元素**
- 阴影效果: `box-shadow` 转换为 PowerPoint 阴影
- 圆角矩形: `border-radius` 支持
- 渐变背景: 预渲染为 PNG 图片
- 装饰线条: 精确宽度和颜色

**4. 18 种专业配色方案**
```
Classic Blue, Teal & Coral, Bold Red, Warm Blush,
Burgundy Luxury, Deep Purple & Emerald, Cream & Forest Green,
Pink & Purple, Lime & Plum, Black & Gold, Sage & Terracotta,
Charcoal & Red, Vibrant Orange, Forest Green, Retro Rainbow,
Vintage Earthy, Coastal Rose, Orange & Turquoise
```

**5. 布局创新**
- 对角线分割
- 非对称列宽 (30/70, 40/60)
- 旋转文本 (90°/270°)
- 重叠形状创造深度
- 全出血图片 + 文字叠加

##### 5.15.3 升级实现计划

**Phase 5.12.1: 专业排版系统**

```python
class ProfessionalTypography:
    """专业排版参数"""

    # 字体大小 (pt)
    TITLE_SIZE = Pt(44)           # 封面标题
    SECTION_TITLE_SIZE = Pt(40)   # 章节标题
    SLIDE_TITLE_SIZE = Pt(32)     # 幻灯片标题
    SUBTITLE_SIZE = Pt(24)        # 副标题
    BODY_SIZE = Pt(20)            # 正文
    CAPTION_SIZE = Pt(14)         # 说明文字

    # 行间距
    LINE_SPACING = 1.5            # 1.5 倍行高

    # 段落间距 (pt)
    PARA_SPACE_BEFORE = Pt(6)
    PARA_SPACE_AFTER = Pt(12)

    # 列表缩进
    BULLET_INDENT = Inches(0.25)
    TEXT_INDENT = Inches(0.5)
```

**Phase 5.12.2: 增强形状系统**

```python
class EnhancedShapes:
    """增强形状效果"""

    def add_shadow(self, shape, shadow_type="outer"):
        """添加阴影效果"""
        # 外阴影: 2px 2px 8px rgba(0,0,0,0.3)
        pass

    def add_rounded_rect(self, slide, x, y, w, h, radius=0.1):
        """添加圆角矩形"""
        pass

    def add_gradient_shape(self, slide, x, y, w, h, colors):
        """添加渐变形状 (预渲染为图片)"""
        pass
```

**Phase 5.12.3: 专业配色系统升级**

```python
PROFESSIONAL_THEMES = {
    "modern_business": {
        "background": "FFFFFF",
        "title": "1E3A8A",
        "subtitle": "64748B",
        "text": "1E293B",
        "accent": "3B82F6",
        "accent2": "60A5FA",
        "decorLine": "3B82F6",
        "shadow": "000000",
        "shadowOpacity": 0.15,
    },
    "classic_blue": {
        "background": "F4F6F6",
        "title": "1C2833",
        "subtitle": "2E4053",
        "text": "2E4053",
        "accent": "AAB7B8",
        "accent2": "1C2833",
        "decorLine": "1C2833",
        "shadow": "1C2833",
        "shadowOpacity": 0.2,
    },
    "teal_coral": {
        "background": "FFFFFF",
        "title": "277884",
        "subtitle": "5EA8A7",
        "text": "2C3E50",
        "accent": "FE4447",
        "accent2": "5EA8A7",
        "decorLine": "FE4447",
        "shadow": "277884",
        "shadowOpacity": 0.15,
    },
    # ... 更多专业配色
}
```

**Phase 5.12.4: 布局增强**

| 布局类型 | 增强内容 |
|---------|---------|
| title_cover | 居中标题 + 装饰线 + 副标题 + 可选背景图 |
| title_section | 大号标题 + 装饰线 + 章节编号 |
| bullet_points | 圆点标记 + 适当缩进 + 行间距优化 |
| two_column | 非对称列宽 + 分隔线 + 独立标题 |
| quote_center | 大引号装饰 + 斜体引用 + 来源署名 |
| thank_you | 装饰线 + 大标题 + 联系信息 |
| image_left/right | 图片阴影 + 文字叠加效果 |
| metric_card | 大数字 + 单位 + 描述 + 卡片阴影 |

**Phase 5.12.5: 高级功能**

- [ ] 图片阴影效果
- [ ] 形状圆角支持
- [ ] 渐变背景 (预渲染)
- [ ] 表格样式增强
- [ ] 图表集成 (基础)
- [ ] 动画效果 (入场动画)
- [ ] 母版/模板系统
- [ ] 缩略图生成

##### 5.15.4 实现优先级

| 优先级 | 功能 | 预计工时 |
|--------|------|---------|
| P0 | 专业排版参数 | 2h |
| P0 | 增强配色系统 | 1h |
| P0 | 布局优化 (6种核心布局) | 4h |
| P1 | 阴影效果 | 2h |
| P1 | 圆角矩形 | 1h |
| P2 | 渐变背景 | 2h |
| P2 | 表格样式 | 2h |
| P3 | 动画效果 | 4h |

##### 5.15.5 测试计划

| 测试类型 | 测试内容 | 验收标准 |
|---------|---------|---------|
| 视觉测试 | 封面页排版 | 标题居中，装饰线美观 |
| 视觉测试 | 内容页排版 | 列表间距适当，易读性好 |
| 视觉测试 | 主题配色 | 颜色协调，对比度足够 |
| 兼容性测试 | PowerPoint 打开 | 无错误，格式正确 |
| 兼容性测试 | WPS 打开 | 无错误，格式正确 |
| 性能测试 | 20 页 PPT 导出 | < 5 秒 |

---

##### 5.15.6 开发进度记录

> **记录时间**: 2026-01-23

| 任务 | 状态 | 说明 |
|------|------|------|
| 专业排版系统 | ✅ 已完成 | ProfessionalTypography 类，字体层次 48/44/36/20pt |
| 增强配色系统 | ✅ 已完成 | 18 种主题配色，8 个颜色属性 |
| 布局优化 | ❌ 未达预期 | 紧凑标题区，但整体视觉效果差 |
| 测试 | ✅ 通过 | 24 项自动化测试通过 |

###### 专业设计师评价

**总体评分: 2/10 - 不可用于商用**

| 页面类型 | 评分 | 问题描述 |
|----------|------|----------|
| **封面页** | 6/10 | 尚可，标题居中，但缺乏视觉冲击力 |
| **目录页** | 2/10 | 列表项松散，无序号或装饰，层次不清晰 |
| **内容页(少)** | 1/10 | 内容漂浮，与标题脱节，大量空白无设计感 |
| **内容页(多)** | 2/10 | 列表项间距僵硬，缺乏呼吸感 |
| **双栏页** | 3/10 | 栏宽不够均衡，无分隔设计 |
| **结束页** | 5/10 | 基本合格，双装饰线略显刻意 |

###### 核心设计缺陷

1. **空间滥用** - 大量无意义空白，没有形成视觉引导
2. **缺乏层次** - 所有元素都是平铺，没有主次之分
3. **装饰空洞** - 装饰线只是简单线条，没有设计意义
4. **色彩单一** - 只用了单色填充，无渐变、无阴影、无质感
5. **排版僵硬** - 纯靠硬编码位置，无法适应不同内容

###### 与专业 PPT 的差距

| 方面 | 专业 PPT | 当前实现 | 差距 |
|------|----------|----------|------|
| 视觉层次 | 明确的主次关系 | 平面化 | 大 |
| 空间利用 | 每寸空间有目的 | 大片空白 | 大 |
| 装饰元素 | 图标、形状、阴影配合 | 单线条 | 大 |
| 色彩应用 | 渐变、透明度、配色 | 纯色填充 | 大 |
| 排版灵活性 | 内容驱动布局 | 固定位置 | 大 |

###### 根本原因分析

**技术架构层面的根本问题**:

1. **缺乏视觉反馈机制**
   - python-pptx 无法预览渲染效果
   - 无法根据实际内容动态调整
   - "盲人摸象"式的开发方式

2. **与 pptx-skills 的本质差距**
   - pptx-skills: HTML → 浏览器渲染 → 提取精确位置 → PPT
   - 当前实现: 硬编码位置 → 直接生成
   - **差距**: 缺少"视觉验证"环节

3. **设计理念的缺失**
   - 只关注"功能实现"，没有"美学设计"
   - 缺乏专业设计规范（网格系统、黄金比例等）

###### 结论

**当前 PPTX 导出功能不适用于生产环境。**

建议方向：
- **短期**: 接受当前限制，作为"基础导出"功能提供
- **中期**: 引入 HTML 预渲染机制，参考 pptx-skills
- **长期**: 考虑与专业设计工具集成，或使用模板系统

###### 已提交的 Git 记录

```
f03b070 - fix(presentation): 优化 PPTX 布局减少空白区域
93e4a83 - fix(presentation): 改进内容页垂直居中布局
379a7b6 - fix(presentation): 修复内容页垂直居中算法
f50dcca - feat(presentation): 升级为专业级 PPTX 导出服务
```

###### 功能可用性评估

| 评估项 | 状态 | 说明 |
|--------|------|------|
| **功能性** | ✅ | 能生成可打开的 PPTX 文件 |
| **美观性** | ❌ | 不符合现代设计审美 |
| **可用性** | ⚠️ | 仅作为草稿级导出 |
| **商用性** | ❌ | 不适合对外使用 |




---

## 十、风险评估与应对

### 10.1 技术风险

| 风险 | 可能性 | 影响 | 应对措施 |
|------|--------|------|---------|
| Milvus 学习曲线 | 中 | 中 | 提前学习文档，准备 ChromaDB 回退方案 |
| Whisper 性能问题 | 中 | 低 | 使用 base 模型，考虑 API 服务回退 |
| MinerU API 不稳定 | 中 | 中 | 实现默认解析方案作为 fallback |
| 前后端集成问题 | 中 | 中 | 定义清晰 API 接口，渐进式开发 |
| SSE 流式传输兼容性 | 低 | 高 | 测试多浏览器，准备 WebSocket 备选 |

### 10.2 资源风险

| 风险 | 可能性 | 影响 | 应对措施 |
|------|--------|------|---------|
| 开发时间不足 | 中 | 高 | 按优先级砍需求，Phase 3 可延后 |
| 服务器资源不足 | 低 | 中 | 优化配置，考虑云服务 |
| API 额度限制 | 中 | 中 | 实现请求缓存，添加限流 |

### 10.3 回退方案

| 功能 | 主方案 | 回退方案 |
|------|--------|---------|
| 向量存储 | Milvus | ChromaDB (现有) |
| 语音识别 | faster-whisper (本地) | Web Speech API (浏览器) |
| 语音合成 | Edge TTS | pyttsx3 (本地) |
| 文档解析 | MinerU API | PyPDF2 + 基础分块 |
| 重排序 | bge-reranker | 无重排序 |

---

## 十一、验收标准

### 11.1 功能验收

| 功能 | 验收条件 |
|------|---------|
| **用户注册** | 能成功注册新用户，密码加密存储 |
| **用户登录** | 能登录并获取 JWT Token |
| **会话管理** | 能创建、切换、删除会话 |
| **流式聊天** | 消息实时流式显示，支持中断 |
| **工具调用** | 工具执行过程可视化，状态正确 |
| **图片理解** | 能上传图片并获得分析结果 |
| **语音输入** | 能录音并转换为文字 |
| **语音输出** | AI 回复能转换为语音播放 |
| **文档上传** | 能上传 PDF 并解析入库 |
| **混合检索** | 能检索到相关内容并显示引用 |
| **Docker 部署** | docker-compose up 一键启动 |
| **AI 生成 PPT** | 能根据主题生成演示文稿并预览/下载 |

### 11.2 性能验收

| 指标 | 目标值 | 测试方法 |
|------|--------|---------|
| 首屏加载 | < 2s | Lighthouse |
| 登录响应 | < 500ms | API 测试 |
| 流式首 Token | < 1s | 手动测试 |
| 检索延迟 | < 500ms | API 测试 |
| 并发用户 | 100+ | 压力测试 |

### 11.3 质量验收

- [ ] 所有 API 有 OpenAPI 文档
- [ ] 关键路径有单元测试
- [ ] 无严重安全漏洞
- [ ] 错误提示用户友好
- [ ] 移动端可正常使用

---

## 十二、附录

### 12.1 参考资料

| 资源 | 链接 |
|------|------|
| Next.js 文档 | https://nextjs.org/docs |
| shadcn/ui | https://ui.shadcn.com |
| Tailwind CSS | https://tailwindcss.com |
| FastAPI | https://fastapi.tiangolo.com |
| Milvus | https://milvus.io/docs |
| faster-whisper | https://github.com/guillaumekln/faster-whisper |
| Edge TTS | https://github.com/rany2/edge-tts |
| MinerU | https://github.com/opendatalab/MinerU |

### 12.2 术语表

| 术语 | 说明 |
|------|------|
| SSE | Server-Sent Events，服务器推送事件 |
| JWT | JSON Web Token，认证令牌 |
| RAG | Retrieval-Augmented Generation，检索增强生成 |
| RRF | Reciprocal Rank Fusion，排名融合算法 |
| BM25 | Best Matching 25，经典检索算法 |
| OCR | Optical Character Recognition，光学字符识别 |
| TTS | Text-to-Speech，文字转语音 |
| STT | Speech-to-Text，语音转文字 |

### 12.3 变更历史

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|---------|------|
| 1.0 | 2025-12-31 | 初始版本 | Claude Code |
| 1.1 | 2025-12-31 | Week 1 完成：Next.js 前端基础架构 | Claude Code |
| 1.2 | 2025-12-31 | Week 2 完成：auth-service 用户认证服务 | Claude Code |
| 1.3 | 2025-12-31 | Week 3 进行中：chat-service 后端完成 | Claude Code |
| 1.4 | 2025-12-31 | Week 3 完成：前端 SSE 流式对接、工具可视化、代码高亮、图表渲染组件 | Claude Code |
| 1.5 | 2025-12-31 | Week 3 完成：修复工具导入路径、UTF-8 中文乱码、OpenAI 兼容模式支持 | Claude Code |
| 1.6 | 2026-01-01 | Week 4 完成：图片理解多模态功能 | Claude Code |
| 1.7 | 2026-01-01 | Week 4 Bug修复：E2B图表显示(变量名冲突)、Markdown图片渲染 | Claude Code |
| 1.8 | 2026-01-01 | 优化 System Prompt：E2B沙箱指南、代码格式规则；新增 Phase 5 AI生成PPT规划 | Claude Code |
| 1.9 | 2026-01-01 | Week 5 完成：语音交互功能 (whisper-service + faster-whisper + edge-tts + 前端组件) | Claude Code |
| 2.0 | 2026-01-02 | Week 5.5 完成：前端侧边栏优化 (ConversationItem组件、Grid布局、默认页面重定向) | Claude Code |
| 2.1 | 2026-01-02 | Week 6 进行中：创建 rag-service 微服务 (Milvus+BM25+RRF混合检索) | Claude Code |
| 2.2 | 2026-01-02 | Week 6 完成：PDF解析(PyPDF2)、SQLite测试模式修复、BM25中文搜索测试通过 | Claude Code |
| 2.3 | 2026-01-02 | Week 7 进行中：Reranker重排序、引用追溯(CitationService)、Milvus空指针修复 | Claude Code |
| 2.4 | 2026-01-02 | Week 7 进行中：智能分块服务(ChunkingService - 语义/页面感知/递归策略) | Claude Code |
| 2.5 | 2026-01-02 | Week 7 进行中：前端引用展示组件(CitationPanel + RAG API + chatStore集成) | Claude Code |
| 2.6 | 2026-01-03 | Week 7 进行中：文档管理界面(DocumentsPage - Tabs组件/上传/列表/删除) | Claude Code |
| 2.7 | 2026-01-03 | Week 7 完成：RAG与Chat集成(rag_search + list_knowledge_documents工具，代理绕过修复) | Claude Code |
| 2.8 | 2026-01-03 | Week 7 完成：RAG检索优化(chunk_size 500→1500, overlap 50→200, top_k 5→10) | Claude Code |
| 2.9 | 2026-01-03 | Week 7 完成：LLM RAG结果利用优化(System Prompt + 引用数据传递 + citation SSE事件) | Claude Code |
| 3.0 | 2026-01-03 | Week 7 完成：文档目录提取功能(extract_toc + chunk_with_toc) + 前端文档列表UI修复 | Claude Code |
| 3.1 | 2026-01-03 | Week 8 规划：新增 Render + Supabase 云部署方案 (pgvector 替代 Milvus) | Claude Code |
| 3.2 | 2026-01-03 | Week 8 实现：PgvectorService 完成 (SQLite暴力搜索 + PostgreSQL pgvector双模式支持) | Claude Code |
| 3.3 | 2026-01-03 | Week 8 完成：Supabase Schema (database/supabase_schema.sql) + Render 部署配置 (render.yaml) | Claude Code |
| 3.4 | 2026-01-03 | Week 8 完成：前端构建配置 (Dockerfile + next.config.ts + API客户端优化 + 类型修复) | Claude Code |
| 3.5 | 2026-01-03 | Week 8 完成：端到端测试脚本 (test_e2e.py + health_check.py + pytest.ini) | Claude Code |
| 3.6 | 2026-01-03 | Week 8 修复：前端 API 路由配置 (.env.local + auth.ts 使用 authApiClient) | Claude Code |
| 3.7 | 2026-01-03 | Week 8 修复：Token Refresh 500 错误 (添加 jti 确保 token 唯一性) | Claude Code |
| 3.8 | 2026-01-03 | Week 8 修复：工具调用/引用持久化 (后端 citation 收集 + 前端字段名驼峰匹配) | Claude Code |
| 3.9 | 2026-01-03 | Phase 5.1 完成：AI生成PPT功能 (generate_presentation工具 + Reveal.js + 前端PresentationPreview组件) | Claude Code |
| 4.0 | 2026-01-03 | Phase 5.1 修复：PPT预览不显示 (agent_service.py 保护 [PRESENTATION_HTML:] 标记不被截断) | Claude Code |
| 4.1 | 2026-01-03 | Phase 5.1 修复：PPT中文乱码 (前端使用 TextDecoder 正确解码 UTF-8 base64) | Claude Code |
| 4.2 | 2026-01-03 | Phase 5 规划：AI生成PPT完整方案 (15+布局类型、图片集成、主题系统、迭代优化) | Claude Code |
| 4.3 | 2026-01-03 | Phase 5 重构：采用方案 B - 独立 presentation-service 架构 (完整设计文档) | Claude Code |
| 4.4 | 2026-01-03 | Phase 5.2 完成：独立服务基础设施 (数据模型/CRUD/编辑器API/AI生成/SQLite兼容) | Claude Code |
| 4.5 | 2026-01-03 | Phase 5.3 完成：前端独立页面 (列表/编辑器/预览/状态管理/组件补齐) | Claude Code |
| 4.6 | 2026-01-03 | Phase 5.4 规划：在线编辑器功能 (实时编辑/插入删除幻灯片/自动保存) | Claude Code |
| 4.7 | 2026-01-03 | Phase 5.5 规划：AI 对话式修改 (自然语言指令解析/多轮对话/AI自动修改PPT) | Claude Code |
| 4.8 | 2026-01-04 | Phase 5.4 完成：在线编辑器功能 (实时编辑/插入删除/自动保存防抖/SQLAlchemy JSON更新修复) | Claude Code |
| 4.9 | 2026-01-04 | Phase 5.4 修复：SQLite 数据库查询类型不匹配 (String vs UUID 对象比较问题) | Claude Code |
| 5.0 | 2026-01-04 | Phase 5.5 完成：AI 对话式修改基础功能 (IntentParserService + AssistantPanel + 14项测试全通过) | Claude Code |
| 5.1 | 2026-01-04 | Phase 5.5 修复：AI 助手对话记录消失问题 (db.commit + 静默更新 + ScrollArea 修复) | Claude Code |
| 5.2 | 2026-01-06 | Phase 5.7 完成：高级生成功能 (布局引擎19种/图片服务Unsplash/主题系统12种/测试113项全通过) | Claude Code |
| 5.3 | 2026-01-06 | Phase 5.8 完成：导出 HTML 功能 (ExportService + 导出API + 34项测试全通过) | Claude Code |
| 5.4 | 2026-01-06 | Phase 5.8 完成：前端导出按钮集成 (下拉菜单/下载HTML/浏览器预览) | Claude Code |
| 5.5 | 2026-01-07 | Bug 修复：AuthProvider 初始化问题 (React 18 Strict Mode 下 useRef 导致页面卡在 Loading) | Claude Code |
| 5.6 | 2026-01-07 | Bug 修复：导出 HTML 中文文件名编码 (RFC 5987 filename* 参数支持 UTF-8) | Claude Code |
| 5.7 | 2026-01-07 | Bug 修复：JWT_SECRET 不一致 (presentation-service 与 auth-service 密钥同步) | Claude Code |
| 5.8 | 2026-01-07 | Phase 5.9 规划：美学优化与 Bug 修复 (HTML结构/主题增强/图片集成/智能匹配) | Claude Code |
| 5.9 | 2026-01-07 | Phase 5.9.1 完成：Bug 修复 (HTML列表标签/Markdown换行符/封面页标题层级) | Claude Code |
| 6.0 | 2026-01-07 | Phase 5.9.2 完成：二次元/动漫主题 (anime_dark/anime_cute/cyberpunk/eva_nerv/retro_pixel) + 智能主题匹配 | Claude Code |
| 6.1 | 2026-01-07 | Phase 5.9.3 完成：AI 生成流程集成图片服务 + 自动主题推荐 (auto_theme 参数) | Claude Code |
| 6.2 | 2026-01-07 | 前端主题选择器更新：17 种主题分类显示 + Next.js rewrites 代理配置 + 前后端联调问题解决方案文档 | Claude Code |
| 6.3 | 2026-01-07 | Bug 修复：PPT 生成时图片不显示 (前端 includeImages 参数从 false 改为 true) | Claude Code |
| 6.4 | 2026-01-07 | Bug 修复：Unsplash Source 服务已停止 (503)，改用 Picsum Photos 作为备用图片源 | Claude Code |
| 6.5 | 2026-01-08 | Phase 5.10 规划：PPT 美学优化方案 (移除随机图片/优化纯文字布局/增强视觉层次) | Claude Code |

---
---

> **文档状态**: ⚠️ Phase 5.12 基础功能完成，美学质量不达标
> **最后更新**: 2026-01-23
> **建议**: 保持当前版本作为基础导出，后续重构需引入预渲染机制