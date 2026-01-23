# ============================================================
# PPTX Renderer Service - Main Entry Point
# ============================================================
"""
PPTX 渲染服务主入口

将 HTML 幻灯片转换为 PPTX 文件的微服务
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api import api_router
from app.services.html_renderer import close_renderer_service

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info(f"启动 {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"监听地址: {settings.HOST}:{settings.PORT}")

    yield

    # 关闭时清理 Playwright 资源
    logger.info("正在关闭 Playwright 浏览器...")
    await close_renderer_service()
    logger.info("服务已关闭")


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="HTML 幻灯片到 PPTX 的渲染服务",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS 配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册 API 路由
    app.include_router(api_router, prefix="/api")

    # 健康检查端点
    @app.get("/health")
    async def health_check():
        """健康检查"""
        return {
            "status": "healthy",
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
        }

    # 根路径
    @app.get("/")
    async def root():
        """根路径"""
        return {
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "health": "/health",
        }

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
