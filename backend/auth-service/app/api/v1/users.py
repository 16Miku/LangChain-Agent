# ============================================================
# Auth Service - User Routes
# ============================================================

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserResponse, UserUpdate, PasswordChange
from app.services.user_service import UserService
from app.core.deps import get_db, get_current_user
from app.models.user import User


router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
)
async def get_profile(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    """
    Get the current authenticated user's profile.

    Requires authentication.
    """
    return UserResponse.model_validate(current_user)


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update current user profile",
)
async def update_profile(
    update_data: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    """
    Update the current authenticated user's profile.

    Requires authentication.
    """
    service = UserService(db)

    # Check if new username is taken
    if update_data.username and update_data.username != current_user.username:
        existing = await service.get_user_by_username(update_data.username)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )
        current_user.username = update_data.username

    # Check if new email is taken
    if update_data.email and update_data.email != current_user.email:
        existing = await service.get_user_by_email(update_data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        current_user.email = update_data.email

    await db.flush()
    await db.refresh(current_user)

    return UserResponse.model_validate(current_user)


@router.put(
    "/me/password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Change password",
)
async def change_password(
    password_data: PasswordChange,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """
    Change the current authenticated user's password.

    Requires authentication. All refresh tokens will be revoked.
    """
    service = UserService(db)

    success = await service.update_password(
        current_user,
        password_data.current_password,
        password_data.new_password,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )


@router.post(
    "/me/logout-all",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout from all devices",
)
async def logout_all_devices(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """
    Revoke all refresh tokens for the current user, effectively logging out
    from all devices.

    Requires authentication.
    """
    service = UserService(db)
    await service.revoke_all_user_tokens(current_user.id)
