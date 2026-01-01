# Whisper and TTS Service Manager
# 语音识别和语音合成服务管理器

import asyncio
import io
import logging
from typing import Optional, Tuple
from faster_whisper import WhisperModel
import edge_tts

from app.config import settings

logger = logging.getLogger(__name__)


class WhisperManager:
    """Whisper 语音识别管理器"""

    def __init__(self):
        self._model: Optional[WhisperModel] = None
        self._lock = asyncio.Lock()
        self._loading = False

    async def get_model(self, model_size: Optional[str] = None) -> WhisperModel:
        """获取 Whisper 模型（懒加载）"""
        model_size = model_size or settings.WHISPER_MODEL_SIZE

        async with self._lock:
            # 如果已加载且模型大小匹配，直接返回
            if self._model is not None:
                return self._model

            # 防止重复加载
            if self._loading:
                # 等待加载完成
                for _ in range(50):  # 最多等5秒
                    await asyncio.sleep(0.1)
                    if self._model is not None:
                        return self._model
                raise RuntimeError("Whisper 模型加载超时")

            self._loading = True

            try:
                logger.info(f"📦 正在加载 Whisper 模型: {model_size}...")
                # 在线程池中加载模型，避免阻塞事件循环
                loop = asyncio.get_event_loop()
                self._model = await loop.run_in_executor(
                    None,
                    lambda: WhisperModel(
                        model_size,
                        device=settings.WHISPER_DEVICE,
                        compute_type=settings.WHISPER_COMPUTE_TYPE
                    )
                )
                logger.info(f"✅ Whisper 模型加载完成: {model_size}")
                return self._model
            except Exception as e:
                logger.error(f"❌ Whisper 模型加载失败: {e}")
                raise
            finally:
                self._loading = False

    async def transcribe(
        self,
        audio_data: bytes,
        language: str = "auto",
        model_size: Optional[str] = None
    ) -> Tuple[str, str, float]:
        """
        转录音频

        Args:
            audio_data: 音频数据 (bytes)
            language: 语言代码 (auto, zh, en, etc.)
            model_size: 模型大小

        Returns:
            (text, detected_language, duration)
        """
        model = await self.get_model(model_size)

        # 将 language="auto" 转换为 None
        lang = None if language == "auto" else language

        # 在线程池中执行转录
        loop = asyncio.get_event_loop()

        def _transcribe():
            # 将 bytes 转换为 BytesIO 对象（类文件对象）
            audio_file = io.BytesIO(audio_data)
            segments, info = model.transcribe(
                audio_file,
                language=lang,
                beam_size=5,
                vad_filter=True,  # 语音活动检测过滤
                vad_parameters=dict(min_silence_duration_ms=500)
            )

            text_parts = []
            for segment in segments:
                text_parts.append(segment.text)

            return "".join(text_parts), info.language, info.duration

        text, detected_lang, duration = await loop.run_in_executor(None, _transcribe)

        logger.info(f"🎤 转录完成: 语言={detected_lang}, 时长={duration:.2f}s, 文字长度={len(text)}")

        return text, detected_lang, duration


class TTSManager:
    """Edge TTS 语音合成管理器"""

    # 常用语音列表
    AVAILABLE_VOICES = {
        "zh-CN-XiaoxiaoNeural": {"name": "晓晓 (女)", "lang": "zh-CN", "gender": "Female"},
        "zh-CN-YunxiNeural": {"name": "云希 (男)", "lang": "zh-CN", "gender": "Male"},
        "zh-CN-YunyangNeural": {"name": "云扬 (男)", "lang": "zh-CN", "gender": "Male"},
        "zh-CN-XiaoyiNeural": {"name": "晓伊 (女)", "lang": "zh-CN", "gender": "Female"},
        "zh-CN-YunjianNeural": {"name": "云健 (男)", "lang": "zh-CN", "gender": "Male"},
        "en-US-JennyNeural": {"name": "Jenny (女)", "lang": "en-US", "gender": "Female"},
        "en-US-GuyNeural": {"name": "Guy (男)", "lang": "en-US", "gender": "Male"},
        "ja-JP-NanamiNeural": {"name": "Nanami (女)", "lang": "ja-JP", "gender": "Female"},
        "ja-JP-KeitaNeural": {"name": "Keita (男)", "lang": "ja-JP", "gender": "Male"},
        "ko-KR-SunHiNeural": {"name": "SunHi (女)", "lang": "ko-KR", "gender": "Female"},
        "ko-KR-InJoonNeural": {"name": "InJoon (男)", "lang": "ko-KR", "gender": "Male"},
    }

    @classmethod
    def get_available_voices(cls, language: Optional[str] = None) -> list[dict]:
        """获取可用语音列表"""
        voices = []
        for voice_id, info in cls.AVAILABLE_VOICES.items():
            if language is None or info["lang"] == language:
                voices.append({
                    "id": voice_id,
                    "name": info["name"],
                    "language": info["lang"],
                    "description": f"{info['name']} - {info['lang']}",
                    "gender": info["gender"]
                })
        return voices

    async def synthesize(
        self,
        text: str,
        voice: str = "zh-CN-XiaoxiaoNeural",
        rate: str = "+0%",
        volume: str = "+0%",
        pitch: str = "+0Hz"
    ) -> bytes:
        """
        文字转语音

        Args:
            text: 要转换的文字
            voice: 语音名称
            rate: 语速
            volume: 音量
            pitch: 音调

        Returns:
            MP3 音频数据 (bytes)
        """
        if voice not in self.AVAILABLE_VOICES:
            logger.warning(f"⚠️ 语音 {voice} 不可用，使用默认语音")
            voice = settings.TTS_DEFAULT_VOICE

        # 在线程池中执行 TTS
        loop = asyncio.get_event_loop()

        def _synthesize():
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice,
                rate=rate,
                volume=volume,
                pitch=pitch
            )
            # edge_tts 使用 save() 方法或生成器获取音频数据
            audio_chunks = []
            for chunk in communicate.stream_sync():
                if chunk["type"] == "audio":
                    audio_chunks.append(chunk["data"])
            return b"".join(audio_chunks)

        audio_data = await loop.run_in_executor(None, _synthesize)

        logger.info(f"🔊 TTS 完成: 文字长度={len(text)}, 语音={voice}, 大小={len(audio_data)} bytes")

        return audio_data


# 全局单例
whisper_manager = WhisperManager()
tts_manager = TTSManager()
