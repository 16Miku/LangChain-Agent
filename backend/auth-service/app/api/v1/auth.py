# ============================================================
# Auth Service - Authentication Routes
# ============================================================

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.schemas.token import TokenResponse, TokenRefresh
from app.services.user_service import UserService
from app.core.deps import get_db, get_current_user
from app.core.security import verify_token
from app.models.user import User


router = APIRouter(prefix="/auth", tags=["Authentication"])

# HTTP Bearer token scheme for verify endpoint
security = HTTPBearer()

# 通用错误响应定义
ERROR_RESPONSES = {
    400: {
        "description": "请求参数错误",
        "content": {
            "application/json": {
                "examples": {
                    "email_exists": {"summary": "邮箱已注册", "value": {"detail": "Email already registered"}},
                    "username_exists": {"summary": "用户名已存在", "value": {"detail": "Username already taken"}},
                }
            }
        }
    },
    401: {
        "description": "认证失败",
        "content": {
            "application/json": {
                "examples": {
                    "invalid_credentials": {"summary": "凭证无效", "value": {"detail": "Invalid email or password"}},
                    "invalid_token": {"summary": "令牌无效", "value": {"detail": "Invalid or expired token"}},
                }
            }
        }
    },
    403: {
        "description": "权限不足",
        "content": {
            "application/json": {
                "example": {"detail": "User account is deactivated"}
            }
        }
    },
}


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="用户注册",
    description="""
注册新用户账户。

### 密码要求
- 长度: 8-100 字符
- 必须包含至少一个大写字母
- 必须包含至少一个小写字母
- 必须包含至少一个数字

### 用户名要求
- 长度: 3-50 字符
- 仅支持字母、数字和下划线
""",
    responses={201: {"description": "注册成功"}, **{k: v for k, v in ERROR_RESPONSES.items() if k == 400}},
)
async def register(
    user_data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    """注册新用户账户。"""
    service = UserService(db)

    # Check if user already exists
    exists, reason = await service.check_user_exists(user_data.email, user_data.username)
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=reason,
        )

    # Create user
    user = await service.create_user(user_data)

    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="用户登录",
    description="""
用户登录并获取访问令牌。

### 返回内容
- `access_token`: 访问令牌，有效期 1 小时
- `refresh_token`: 刷新令牌，有效期 7 天
- `expires_in`: 访问令牌过期时间（秒）
""",
    responses={401: ERROR_RESPONSES[401]},
)
async def login(
    login_data: UserLogin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """用户登录并获取访问令牌。"""
    service = UserService(db)

    # Authenticate user
    user = await service.authenticate_user(login_data.email, login_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create tokens
    tokens = await service.create_tokens(user)

    return tokens


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="刷新访问令牌",
    description="""
使用刷新令牌获取新的访问令牌和刷新令牌。

### 注意事项
- 旧的刷新令牌在使用后会失效
- 如果刷新令牌已过期，需要重新登录
""",
    responses={401: ERROR_RESPONSES[401]},
)
async def refresh_token(
    token_data: TokenRefresh,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """使用刷新令牌获取新的访问令牌。"""
    import logging
    logger = logging.getLogger(__name__)

    try:
        service = UserService(db)
        tokens = await service.refresh_tokens(token_data.refresh_token)
        if tokens is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return tokens
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {type(e).__name__}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh failed: {str(e)}",
        )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="用户登出",
    description="""
登出当前设备，撤销指定的刷新令牌。

### 注意事项
- 需要在请求头中携带有效的访问令牌
- 登出后该刷新令牌将无法再使用
""",
    responses={401: ERROR_RESPONSES[401]},
)
async def logout(
    token_data: TokenRefresh,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """登出当前设备，撤销刷新令牌。"""
    service = UserService(db)
    await service.revoke_refresh_token(token_data.refresh_token)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="获取当前用户信息",
    description="获取当前已认证用户的详细信息。需要在请求头中携带有效的访问令牌。",
    responses={401: ERROR_RESPONSES[401]},
)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    """获取当前已认证用户的详细信息。"""
    return UserResponse.model_validate(current_user)


@router.get(
    "/verify",
    summary="验证 JWT 令牌",
    description="""
验证 JWT 令牌并返回用户信息。

### 用途
此接口供其他微服务调用，用于验证用户令牌的有效性。

### 返回内容
- `user_id`: 用户 ID
- `username`: 用户名
- `email`: 邮箱
- `is_active`: 账户状态
""",
    responses={
        200: {
            "description": "令牌有效",
            "content": {
                "application/json": {
                    "example": {
                        "user_id": "550e8400-e29b-41d4-a716-446655440000",
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "username": "john_doe",
                        "email": "john@example.com",
                        "is_active": True
                    }
                }
            }
        },
        401: ERROR_RESPONSES[401],
        403: ERROR_RESPONSES[403],
    },
)
async def verify_token_endpoint(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """验证 JWT 令牌并返回用户信息。"""
    token = credentials.credentials
    payload = verify_token(token, token_type="access")

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    # Get user from database
    from sqlalchemy import select
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )

    return {
        "user_id": str(user.id),
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
    }
