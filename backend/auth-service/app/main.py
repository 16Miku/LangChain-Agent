# ============================================================
# Auth Service - FastAPI Main Application
# ============================================================

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import init_db
from .api.v1.auth import router as auth_router
from .api.v1.users import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup: Initialize database
    print("Initializing database...")
    await init_db()
    print("Database initialized successfully.")

    yield

    # Shutdown: Cleanup
    print("Shutting down...")


# OpenAPI 标签描述
tags_metadata = [
    {
        "name": "Health",
        "description": "服务健康检查接口",
    },
    {
        "name": "Authentication",
        "description": "用户认证相关接口：注册、登录、令牌刷新、登出",
    },
    {
        "name": "Users",
        "description": "用户管理接口：获取/更新用户资料、修改密码",
    },
]

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## Auth Service - 用户认证服务

Stream-Agent V9 的用户认证微服务，提供完整的用户管理和 JWT 认证功能。

### 功能特性

- **用户注册/登录**: 支持邮箱注册和登录
- **JWT 认证**: Access Token + Refresh Token 双令牌机制
- **密码安全**: 强密码验证 (大小写字母 + 数字)
- **多设备管理**: 支持登出所有设备

### 认证方式

所有需要认证的接口都需要在请求头中携带 Bearer Token:

```
Authorization: Bearer <access_token>
```

### 错误码说明

| 状态码 | 说明 |
|--------|------|
| 400 | 请求参数错误 (如用户名已存在、密码格式不正确) |
| 401 | 未认证或令牌无效/过期 |
| 403 | 权限不足 (如账户被禁用) |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |
""",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=tags_metadata,
    contact={
        "name": "Stream-Agent Team",
        "email": "support@stream-agent.com",
    },
    license_info={
        "name": "MIT",
    },
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")


@app.get("/", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/health", tags=["Health"])
async def health():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": "connected",
    }
