# ============================================================
# Presentation Service - Security
# ============================================================

import httpx
from typing import Optional
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings


security = HTTPBearer()


async def verify_token_with_auth_service(
    token: str
) -> Optional[dict]:
    """
    向 auth-service 验证 Token
    """
    try:
        # 显式禁用代理，避免 Clash 等软件干扰本地请求
        # 同时设置 trust_env=False 防止读取环境变量中的代理设置
        # 增加 limits 以提高性能
        limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
        async with httpx.AsyncClient(
            timeout=10.0,
            limits=limits,
            proxy=None,
            trust_env=False  # 关键：不读取环境变量中的代理设置
        ) as client:
            response = await client.get(
                f"{settings.AUTH_SERVICE_URL}/api/auth/verify",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                return response.json()
            return None
    except Exception as e:
        if settings.DEBUG:
            print(f"Token verification error: {type(e).__name__}: {e}")
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> dict:
    """
    获取当前用户信息
    验证 JWT Token 并返回用户数据
    """
    token = credentials.credentials

    # 向 auth-service 验证 Token
    user_data = await verify_token_with_auth_service(token)

    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_data


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> str:
    """
    获取当前用户 ID
    简化版本，仅返回用户 ID
    """
    user_data = await get_current_user(credentials)
    return user_data.get("user_id", user_data.get("id", ""))


# 可选的认证依赖（用于开发调试）
async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(HTTPBearer(auto_error=False))
) -> Optional[dict]:
    """
    可选的认证依赖
    如果没有提供 Token，返回 None
    """
    if credentials is None:
        return None

    token = credentials.credentials
    user_data = await verify_token_with_auth_service(token)

    if not user_data:
        return None

    return user_data
