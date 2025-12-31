# ============================================================
# Auth Service - User Service
# ============================================================

from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.models.user import User, RefreshToken
from app.schemas.user import UserCreate
from app.schemas.token import TokenResponse
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    hash_token,
    get_token_expiration,
)
from app.config import settings


class UserService:
    """Service class for user-related operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def check_user_exists(self, email: str, username: str) -> tuple[bool, str]:
        """
        Check if user with given email or username already exists.

        Returns:
            Tuple of (exists: bool, reason: str)
        """
        result = await self.db.execute(
            select(User).where(
                or_(User.email == email, User.username == username)
            )
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            if existing_user.email == email:
                return True, "Email already registered"
            return True, "Username already taken"

        return False, ""

    async def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user.

        Args:
            user_data: User creation data

        Returns:
            Created user object
        """
        user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=get_password_hash(user_data.password),
        )

        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)

        return user

    async def authenticate_user(
        self, email: str, password: str
    ) -> Optional[User]:
        """
        Authenticate user with email and password.

        Args:
            email: User email
            password: Plain text password

        Returns:
            User object if authentication successful, None otherwise
        """
        user = await self.get_user_by_email(email)

        if user is None:
            return None

        if not verify_password(password, user.password_hash):
            return None

        if not user.is_active:
            return None

        return user

    async def create_tokens(self, user: User) -> TokenResponse:
        """
        Create access and refresh tokens for a user.

        Args:
            user: User object

        Returns:
            TokenResponse with access and refresh tokens
        """
        # Create access token
        access_token = create_access_token(subject=user.id)

        # Create refresh token
        refresh_token = create_refresh_token(subject=user.id)

        # Store refresh token hash in database
        refresh_token_record = RefreshToken(
            user_id=user.id,
            token_hash=hash_token(refresh_token),
            expires_at=get_token_expiration("refresh"),
        )
        self.db.add(refresh_token_record)
        await self.db.flush()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def refresh_tokens(self, refresh_token: str) -> Optional[TokenResponse]:
        """
        Refresh access token using refresh token.

        Args:
            refresh_token: JWT refresh token

        Returns:
            New TokenResponse if valid, None otherwise
        """
        from app.core.security import verify_token

        # Verify the refresh token
        payload = verify_token(refresh_token, token_type="refresh")
        if payload is None:
            return None

        user_id = payload.get("sub")
        if user_id is None:
            return None

        # Check if refresh token exists and is not revoked
        token_hash = hash_token(refresh_token)
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.user_id == user_id,
                RefreshToken.is_revoked == False,
                RefreshToken.expires_at > datetime.utcnow(),
            )
        )
        stored_token = result.scalar_one_or_none()

        if stored_token is None:
            return None

        # Get user
        user = await self.get_user_by_id(user_id)
        if user is None or not user.is_active:
            return None

        # Revoke old refresh token
        stored_token.is_revoked = True

        # Create new tokens
        return await self.create_tokens(user)

    async def revoke_refresh_token(self, refresh_token: str) -> bool:
        """
        Revoke a refresh token.

        Args:
            refresh_token: JWT refresh token to revoke

        Returns:
            True if successfully revoked, False otherwise
        """
        token_hash = hash_token(refresh_token)
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        stored_token = result.scalar_one_or_none()

        if stored_token:
            stored_token.is_revoked = True
            await self.db.flush()
            return True

        return False

    async def revoke_all_user_tokens(self, user_id: str) -> int:
        """
        Revoke all refresh tokens for a user.

        Args:
            user_id: User ID

        Returns:
            Number of tokens revoked
        """
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.is_revoked == False,
            )
        )
        tokens = result.scalars().all()

        for token in tokens:
            token.is_revoked = True

        await self.db.flush()
        return len(tokens)

    async def update_password(
        self, user: User, current_password: str, new_password: str
    ) -> bool:
        """
        Update user password.

        Args:
            user: User object
            current_password: Current plain text password
            new_password: New plain text password

        Returns:
            True if password updated successfully, False otherwise
        """
        if not verify_password(current_password, user.password_hash):
            return False

        user.password_hash = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        await self.db.flush()

        # Revoke all refresh tokens for security
        await self.revoke_all_user_tokens(user.id)

        return True
