# ============================================================
# Chat Service - Dependencies
# ============================================================

from typing import Annotated, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db_session
from app.core.security import verify_token


# HTTP Bearer token scheme
security = HTTPBearer()


class CurrentUser(BaseModel):
    """Current user information extracted from JWT token."""

    id: str
    username: str
    email: str


async def get_db() -> AsyncSession:
    """Database session dependency."""
    async for session in get_db_session():
        yield session


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> CurrentUser:
    """
    Get the current authenticated user from the JWT token.

    This doesn't query the database - it trusts the JWT payload.
    User data is validated by auth-service when issuing the token.

    Args:
        credentials: HTTP Bearer credentials

    Returns:
        CurrentUser object with user info from token

    Raises:
        HTTPException: If token is invalid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    payload = verify_token(token, token_type="access")

    if payload is None:
        raise credentials_exception

    user_id = payload.get("sub")
    username = payload.get("username")
    email = payload.get("email")

    if not user_id:
        raise credentials_exception

    return CurrentUser(
        id=user_id,
        username=username or "",
        email=email or "",
    )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
) -> Optional[CurrentUser]:
    """
    Get the current user if authenticated, None otherwise.

    This is useful for endpoints that work both with and without authentication.

    Args:
        credentials: Optional HTTP Bearer credentials

    Returns:
        CurrentUser if authenticated, None otherwise
    """
    if credentials is None:
        return None

    token = credentials.credentials
    payload = verify_token(token, token_type="access")

    if payload is None:
        return None

    user_id = payload.get("sub")
    username = payload.get("username")
    email = payload.get("email")

    if not user_id:
        return None

    return CurrentUser(
        id=user_id,
        username=username or "",
        email=email or "",
    )
