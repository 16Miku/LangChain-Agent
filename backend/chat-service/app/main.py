# ============================================================
# Chat Service - FastAPI Application
# ============================================================

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.api.v1 import conversations, chat
from app.services.agent_service import cleanup


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}...")
    await init_db()
    print("Database initialized.")

    yield

    # Shutdown
    print("Shutting down...")
    await cleanup()
    print("Cleanup completed.")


# OpenAPI 标签描述
tags_metadata = [
    {
        "name": "Health",
        "description": "服务健康检查接口",
    },
    {
        "name": "chat",
        "description": "聊天接口：流式对话、AI Agent 交互",
    },
    {
        "name": "conversations",
        "description": "会话管理接口：创建、查询、更新、删除会话和消息",
    },
]

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## Chat Service - 聊天服务

Stream-Agent V9 的核心聊天微服务，提供 AI Agent 对话和会话管理功能。

### 功能特性

- **流式对话**: 基于 SSE (Server-Sent Events) 的实时流式响应
- **LangGraph Agent**: 支持 96+ 工具的智能 Agent
- **多模态支持**: 支持图片输入的多模态对话
- **会话管理**: 完整的会话和消息 CRUD 操作
- **工具调用**: 实时展示工具执行状态
- **引用追溯**: RAG 检索结果的引用信息

### SSE 事件类型

| 事件类型 | 说明 |
|----------|------|
| `text` | AI 文本响应 (Base64 编码) |
| `tool_start` | 工具开始执行 |
| `tool_end` | 工具执行完成 |
| `citation` | 引用信息 |
| `done` | 流结束 |
| `error` | 错误信息 |

### 认证方式

所有接口都需要在请求头中携带 Bearer Token:

```
Authorization: Bearer <access_token>
```

### 错误码说明

| 状态码 | 说明 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 未认证或令牌无效 |
| 404 | 会话或消息不存在 |
| 500 | 服务器内部错误 |
""",
    lifespan=lifespan,
    openapi_tags=tags_metadata,
    contact={
        "name": "Stream-Agent Team",
        "email": "support@stream-agent.com",
    },
    license_info={
        "name": "MIT",
    },
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(conversations.router)
app.include_router(chat.router)


@app.get("/")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": "connected",
    }
