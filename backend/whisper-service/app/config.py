# Whisper Service Configuration

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # 服务配置
    SERVICE_NAME: str = "whisper-service"
    SERVICE_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # API 配置
    API_V1_PREFIX: str = "/api/v1"

    # CORS 配置
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8501",
    ]

    # Whisper 配置
    WHISPER_MODEL_SIZE: str = "base"  # tiny, base, small, medium, large
    WHISPER_DEVICE: str = "cpu"  # cpu, cuda
    WHISPER_COMPUTE_TYPE: str = "int8"  # int8, float16, float32

    # 文件上传配置
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_AUDIO_FORMATS: list[str] = [
        "audio/wav",
        "audio/mp3",
        "audio/mpeg",
        "audio/webm",
        "audio/ogg",
        "audio/mp4",
        "audio/x-wav",
        "audio/x-mpeg",
    ]

    # Edge TTS 配置
    TTS_DEFAULT_VOICE: str = "zh-CN-XiaoxiaoNeural"
    TTS_RATE: str = "+0%"  # 语速调整 -50% 到 +100%
    TTS_VOLUME: str = "+0%"  # 音量调整 -50% 到 +100%
    TTS_PITCH: str = "+0Hz"  # 音调调整 -50Hz 到 +50Hz

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
