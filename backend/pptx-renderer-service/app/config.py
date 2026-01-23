# ============================================================
# PPTX Renderer Service - Configuration
# ============================================================

from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """服务配置"""

    # 应用信息
    APP_NAME: str = "PPTX Renderer Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8006

    # CORS 配置
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    # 渲染配置
    DEFAULT_SLIDE_WIDTH: int = 1920
    DEFAULT_SLIDE_HEIGHT: int = 1080
    SCREENSHOT_QUALITY: int = 95

    # Playwright 配置
    PLAYWRIGHT_HEADLESS: bool = True
    PLAYWRIGHT_TIMEOUT: int = 30000  # 30 秒

    # PPTX 配置
    PPTX_SLIDE_WIDTH_INCHES: float = 13.333  # 16:9 宽度
    PPTX_SLIDE_HEIGHT_INCHES: float = 7.5  # 16:9 高度

    @property
    def cors_origins_list(self) -> List[str]:
        """解析 CORS 来源列表"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# 全局配置实例
settings = Settings()
