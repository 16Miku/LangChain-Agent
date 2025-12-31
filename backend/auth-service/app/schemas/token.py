# ============================================================
# Auth Service - Token Schemas
# ============================================================

from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    """Schema for token response after login."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration time in seconds")


class TokenRefresh(BaseModel):
    """Schema for token refresh request."""

    refresh_token: str = Field(..., description="Refresh token to exchange for new tokens")


class TokenPayload(BaseModel):
    """Schema for decoded token payload."""

    sub: str  # User ID
    exp: int  # Expiration timestamp
    type: str  # Token type: "access" or "refresh"
