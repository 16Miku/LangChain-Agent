# ============================================================
# Security - JWT Token Verification
# ============================================================

from typing import Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import BaseModel

from app.config import settings

security = HTTPBearer()


class TokenPayload(BaseModel):
    """Token 载荷"""
    sub: str  # user_id
    username: Optional[str] = None
    email: Optional[str] = None
    exp: int


class CurrentUser(BaseModel):
    """当前用户信息"""
    user_id: str
    username: Optional[str] = None
    email: Optional[str] = None


def verify_token(token: str) -> TokenPayload:
    """验证 JWT Token"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return TokenPayload(**payload)
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> CurrentUser:
    """获取当前用户"""
    token = credentials.credentials
    payload = verify_token(token)

    return CurrentUser(
        user_id=payload.sub,
        username=payload.username,
        email=payload.email
    )
