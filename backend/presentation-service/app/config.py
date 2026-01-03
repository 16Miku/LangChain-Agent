# ============================================================
# Presentation Service - Configuration
# ============================================================

import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""

    # 应用信息
    APP_NAME: str = "Presentation Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8005

    # 数据库配置
    DATABASE_URL: str = "sqlite:///./presentations.db"

    # JWT 配置 (与 auth-service 共享)
    JWT_SECRET: str = "your-jwt-secret-key"
    JWT_ALGORITHM: str = "HS256"

    # Auth Service 地址 (用于验证 Token)
    AUTH_SERVICE_URL: str = "http://localhost:8001"

    # LLM Provider Configuration
    LLM_PROVIDER: str = "openai_compatible"  # "google" or "openai_compatible"

    # Google AI Configuration (备用)
    GOOGLE_API_KEY: str = ""
    GOOGLE_MODEL: str = "gemini-1.5-flash"

    # OpenAI Compatible Configuration (第三方服务商)
    OPENAI_BASE_URL: str = ""
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    # E2B 配置 (用于代码执行和图表)
    E2B_API_KEY: str = ""

    # 图片服务配置
    UNSPLASH_SOURCE_URL: str = "https://source.unsplash.com/featured"
    PEXELS_API_KEY: str = ""

    # CORS 配置
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        """将 CORS_ORIGINS 字符串转换为列表"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()
