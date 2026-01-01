# API Schemas for Whisper Service

from pydantic import BaseModel, Field
from typing import Optional


class TranscribeRequest(BaseModel):
    """语音识别请求"""

    language: Optional[str] = Field(
        default="auto",
        description="语言代码: zh, en, ja, ko, auto (自动检测)",
        pattern="^(auto|zh|en|ja|ko|fr|de|es|ru)$"
    )
    model_size: Optional[str] = Field(
        default="base",
        description="Whisper 模型大小: tiny, base, small, medium, large"
    )


class TranscribeResponse(BaseModel):
    """语音识别响应"""

    text: str = Field(..., description="识别的文字内容")
    language: str = Field(..., description="检测到的语言")
    duration: float = Field(..., description="音频时长（秒）")
    confidence: Optional[float] = Field(None, description="置信度 (0-1)")


class TTSCreateRequest(BaseModel):
    """文字转语音请求"""

    text: str = Field(..., min_length=1, max_length=5000, description="要转换的文字")
    voice: Optional[str] = Field(
        default="zh-CN-XiaoxiaoNeural",
        description="语音名称"
    )
    rate: Optional[str] = Field(
        default="+0%",
        description="语速调整 (-50% 到 +100%)"
    )
    volume: Optional[str] = Field(
        default="+0%",
        description="音量调整 (-50% 到 +50%)"
    )
    pitch: Optional[str] = Field(
        default="+0Hz",
        description="音调调整 (-50Hz 到 +50Hz)"
    )


class VoiceInfo(BaseModel):
    """语音信息"""

    id: str
    name: str
    language: str
    description: str
    gender: str  # Male, Female


class VoicesResponse(BaseModel):
    """可用语音列表响应"""

    voices: list[VoiceInfo]


class HealthResponse(BaseModel):
    """健康检查响应"""

    status: str
    service: str
    version: str
    whisper_loaded: bool
    tts_available: bool
