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


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="演示文稿生成与管理服务",
        lifespan=lifespan,
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
    @app.get("/health")
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
