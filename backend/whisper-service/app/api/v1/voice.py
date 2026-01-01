# Voice API Routes
# 语音相关 API 端点

import io
import logging
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse

from app.schemas import (
    TranscribeResponse,
    TTSCreateRequest,
    VoicesResponse,
    VoiceInfo,
    HealthResponse
)
from app.core.voice_manager import whisper_manager, tts_manager
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["voice"])


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(
    file: UploadFile = File(..., description="音频文件 (wav, mp3, webm, ogg)"),
    language: str = Form(default="auto", description="语言代码: auto, zh, en, ja, ko"),
    model_size: str = Form(default="base", description="模型大小: tiny, base, small, medium, large")
):
    """
    语音转文字 (STT)

    支持的音频格式: WAV, MP3, WebM, OGG
    支持的语言: 中文(zh), 英文(en), 日文(ja), 韩文(ko), 自动检测(auto)
    """
    # 验证文件大小
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"文件过大，最大支持 {settings.MAX_UPLOAD_SIZE // 1024 // 1024}MB"
        )

    # 验证文件类型（宽松检查，允许 codecs 等参数）
    if file.content_type:
        content_type = file.content_type.split(";")[0].strip()  # 去除 codecs 等参数
        if content_type not in settings.ALLOWED_AUDIO_FORMATS:
            # 检查是否为允许的音频格式前缀
            if not any(content_type.startswith(ct.split("/")[0] + "/") for ct in settings.ALLOWED_AUDIO_FORMATS):
                raise HTTPException(
                    status_code=415,
                    detail=f"不支持的音频格式: {file.content_type}"
                )

    try:
        text, detected_lang, duration = await whisper_manager.transcribe(
            audio_data=content,
            language=language,
            model_size=model_size
        )

        return TranscribeResponse(
            text=text.strip(),
            language=detected_lang,
            duration=duration,
            confidence=None  # faster-whisper 不直接提供置信度
        )

    except Exception as e:
        logger.error(f"转录失败: {e}")
        raise HTTPException(status_code=500, detail=f"转录失败: {str(e)}")


@router.post("/synthesize", responses={200: {"content": {"audio/mpeg": b""}}})
async def synthesize_speech(request: TTSCreateRequest):
    """
    文字转语音 (TTS)

    返回 MP3 格式音频流
    """
    try:
        audio_data = await tts_manager.synthesize(
            text=request.text,
            voice=request.voice,
            rate=request.rate,
            volume=request.volume,
            pitch=request.pitch
        )

        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f"attachment; filename=tts.mp3",
                "Content-Length": str(len(audio_data))
            }
        )

    except Exception as e:
        logger.error(f"TTS 失败: {e}")
        raise HTTPException(status_code=500, detail=f"语音合成失败: {str(e)}")


@router.get("/voices", response_model=VoicesResponse)
async def get_voices(language: Optional[str] = None):
    """
    获取可用的语音列表

    可选参数:
    - language: 筛选特定语言的语音 (zh-CN, en-US, ja-JP, ko-KR)
    """
    voices = tts_manager.get_available_voices(language=language)
    return VoicesResponse(
        voices=[
            VoiceInfo(**v)
            for v in voices
        ]
    )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """服务健康检查"""
    # 检查 Whisper 是否可用（不实际加载模型）
    whisper_available = True  # faster-whisper 已安装

    # 检查 TTS 是否可用
    tts_available = True  # edge-tts 已安装

    return HealthResponse(
        status="healthy",
        service=settings.SERVICE_NAME,
        version=settings.SERVICE_VERSION,
        whisper_loaded=whisper_manager._model is not None,
        tts_available=tts_available
    )


@router.get("/info")
async def service_info():
    """服务信息"""
    return {
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "features": {
            "stt": {
                "enabled": True,
                "engine": "faster-whisper",
                "models": ["tiny", "base", "small", "medium", "large"],
                "languages": ["auto", "zh", "en", "ja", "ko", "fr", "de", "es", "ru"],
                "formats": ["wav", "mp3", "webm", "ogg"]
            },
            "tts": {
                "enabled": True,
                "engine": "edge-tts",
                "voices_count": len(tts_manager.AVAILABLE_VOICES),
                "default_voice": settings.TTS_DEFAULT_VOICE
            }
        }
    }
