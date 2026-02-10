# ============================================================
# Presentation Service - Main Entry Point
# ============================================================

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api import api_router
from app.database import engine
from app.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时创建表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # 关闭时清理
    await engine.dispose()


# OpenAPI 标签描述
tags_metadata = [
    {
        "name": "Health",
        "description": "服务健康检查接口",
    },
    {
        "name": "presentations",
        "description": "演示文稿 CRUD 接口：创建、查询、更新、删除、导出",
    },
    {
        "name": "editor",
        "description": "高级编辑接口：AI 生成、主题系统、布局引擎、图片服务",
    },
    {
        "name": "assistant",
        "description": "AI 助手接口：自然语言指令编辑演示文稿",
    },
]


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="""
## Presentation Service - 演示文稿服务

Stream-Agent V9 的演示文稿微服务，提供 AI 生成 PPT 和高级编辑功能。

### 功能特性

- **AI 生成**: 根据主题自动生成完整演示文稿
- **17 种主题**: 企业蓝、科技深色、霓虹未来等精品主题
- **19 种布局**: 封面、章节、列表、对比、时间线等
- **图片服务**: 自动配图、关键词推荐
- **AI 助手**: 自然语言指令编辑
- **多格式导出**: HTML、PPTX

### 主题列表

| 主题 | 风格 | 适用场景 |
|------|------|----------|
| modern_business | 商务 | 企业汇报、商业计划 |
| tech_dark | 科技 | 技术分享、产品发布 |
| neon_future | 未来 | 游戏、电竞、创意 |
| elegant_dark | 高端 | 奢侈品、高端服务 |
| minimal_white | 简约 | 学术、设计、艺术 |
| nature_green | 自然 | 环保、健康、教育 |

### 布局类型

- **cover**: 封面页
- **section**: 章节页
- **bullet_points**: 列表页
- **two_column**: 双栏布局
- **comparison**: 对比布局
- **timeline**: 时间线
- **quote**: 引用页
- **thanks**: 感谢页

### 认证方式

所有接口都需要在请求头中携带 Bearer Token:

```
Authorization: Bearer <access_token>
```

### 错误码说明

| 状态码 | 说明 |
|--------|------|
| 400 | 请求参数错误 (如无效的主题或布局) |
| 401 | 未认证或令牌无效 |
| 404 | 演示文稿不存在 |
| 500 | 服务器内部错误 (如 AI 生成失败) |
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

    # CORS 配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    app.include_router(api_router, prefix="/api")

    # 健康检查
    @app.get("/health", tags=["Health"])
    async def health_check():
        return {"status": "healthy", "service": settings.APP_NAME}

    return app


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
