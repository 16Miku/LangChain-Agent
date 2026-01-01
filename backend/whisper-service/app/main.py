# Whisper Service Main Entry Point
# FastAPI 应用入口

import logging
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.v1.voice import router as voice_router

# 配置日志
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info(f"🚀 启动 {settings.SERVICE_NAME} v{settings.SERVICE_VERSION}")
    logger.info(f"📋 Whisper 模型: {settings.WHISPER_MODEL_SIZE} ({settings.WHISPER_DEVICE})")
    logger.info(f"🔊 TTS 默认语音: {settings.TTS_DEFAULT_VOICE}")

    # 预加载 TTS 信息（不加载 Whisper 模型，懒加载）
    from app.core.voice_manager import tts_manager
    voices = tts_manager.get_available_voices()
    logger.info(f"🎙️  可用语音数量: {len(voices)}")

    yield

    logger.info(f"👋 关闭 {settings.SERVICE_NAME}")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.SERVICE_NAME,
    description="语音识别与语音合成服务 (Powered by faster-whisper & Edge TTS)",
    version=settings.SERVICE_VERSION,
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 路由注册
app.include_router(
    voice_router,
    prefix=f"{settings.API_V1_PREFIX}/voice",
)


@app.get("/")
async def root():
    """根路径"""
    return {
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "status": "running",
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/voice/health"
    }


@app.get("/health")
async def health():
    """简单健康检查"""
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8003,
        reload=settings.DEBUG,
        log_level="info"
    )
