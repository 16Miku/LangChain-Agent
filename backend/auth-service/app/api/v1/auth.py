# ============================================================
# Auth Service - Authentication Routes
# ============================================================

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.schemas.token import TokenResponse, TokenRefresh
from app.services.user_service import UserService
from app.core.deps import get_db, get_current_user
from app.models.user import User


router = APIRouter(prefix="/auth", tags=["Authentication"])


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
    service = UserService(db)

    tokens = await service.refresh_tokens(token_data.refresh_token)
    if tokens is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return tokens


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
