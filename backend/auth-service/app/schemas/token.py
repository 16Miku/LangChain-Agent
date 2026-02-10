# ============================================================
# Auth Service - Token Schemas
# ============================================================

from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    """Schema for token response after login."""

    access_token: str = Field(
        ...,
        description="JWT 访问令牌，用于 API 认证",
        json_schema_extra={"example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
    )
    refresh_token: str = Field(
        ...,
        description="JWT 刷新令牌，用于获取新的访问令牌",
        json_schema_extra={"example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
    )
    token_type: str = Field(
        default="bearer",
        description="令牌类型",
        json_schema_extra={"example": "bearer"}
    )
    expires_in: int = Field(
        ...,
        description="访问令牌过期时间 (秒)",
        json_schema_extra={"example": 3600}
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJleHAiOjE3MDk4MjQwMDAsInR5cGUiOiJhY2Nlc3MifQ.xxx",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJleHAiOjE3MTAzNDI0MDAsInR5cGUiOiJyZWZyZXNoIn0.yyy",
                    "token_type": "bearer",
                    "expires_in": 3600
                }
            ]
        }
    }


class TokenRefresh(BaseModel):
    """Schema for token refresh request."""

    refresh_token: str = Field(
        ...,
        description="刷新令牌，用于换取新的访问令牌和刷新令牌",
        json_schema_extra={"example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJleHAiOjE3MTAzNDI0MDAsInR5cGUiOiJyZWZyZXNoIn0.yyy"
                }
            ]
        }
    }


class TokenPayload(BaseModel):
    """Schema for decoded token payload."""

    sub: str = Field(..., description="用户 ID")
    exp: int = Field(..., description="过期时间戳 (Unix timestamp)")
    type: str = Field(..., description="令牌类型: 'access' 或 'refresh'")
