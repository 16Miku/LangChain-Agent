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


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(
    user_data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    """
    Register a new user account.

    - **username**: Unique username (3-50 characters, alphanumeric and underscores)
    - **email**: Unique email address
    - **password**: Password (8-100 characters, must contain uppercase, lowercase, and digit)
    """
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
    summary="User login",
)
async def login(
    login_data: UserLogin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """
    Authenticate user and return access/refresh tokens.

    - **email**: User email address
    - **password**: User password
    """
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
    summary="Refresh access token",
)
async def refresh_token(
    token_data: TokenRefresh,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """
    Exchange a refresh token for new access and refresh tokens.

    - **refresh_token**: Valid refresh token
    """
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
    summary="User logout",
)
async def logout(
    token_data: TokenRefresh,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """
    Logout user by revoking the refresh token.

    Requires authentication.
    """
    service = UserService(db)
    await service.revoke_refresh_token(token_data.refresh_token)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    """
    Get the current authenticated user's information.

    Requires authentication.
    """
    return UserResponse.model_validate(current_user)


@router.get(
    "/verify",
    summary="Verify JWT token",
)
async def verify_token_endpoint(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """
    Verify a JWT token and return user information.

    This endpoint is used by other services to validate tokens.

    Returns:
        dict with user_id and username if valid
    """
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
