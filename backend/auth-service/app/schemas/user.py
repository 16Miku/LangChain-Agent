# ============================================================
# Auth Service - User Schemas
# ============================================================

from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional
import re


class UserCreate(BaseModel):
    """Schema for user registration."""

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="用户名 (3-50 字符，仅支持字母、数字和下划线)",
        json_schema_extra={"example": "john_doe"}
    )
    email: EmailStr = Field(
        ...,
        description="用户邮箱地址",
        json_schema_extra={"example": "john@example.com"}
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="密码 (8-100 字符，必须包含大写字母、小写字母和数字)",
        json_schema_extra={"example": "SecurePass123"}
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "john_doe",
                    "email": "john@example.com",
                    "password": "SecurePass123"
                }
            ]
        }
    }

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username format."""
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Username can only contain letters, numbers, and underscores")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr = Field(
        ...,
        description="用户邮箱地址",
        json_schema_extra={"example": "john@example.com"}
    )
    password: str = Field(
        ...,
        description="用户密码",
        json_schema_extra={"example": "SecurePass123"}
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "john@example.com",
                    "password": "SecurePass123"
                }
            ]
        }
    }


class UserResponse(BaseModel):
    """Schema for user response."""

    id: str = Field(..., description="用户唯一标识", json_schema_extra={"example": "550e8400-e29b-41d4-a716-446655440000"})
    username: str = Field(..., description="用户名", json_schema_extra={"example": "john_doe"})
    email: str = Field(..., description="邮箱地址", json_schema_extra={"example": "john@example.com"})
    is_active: bool = Field(..., description="账户是否激活", json_schema_extra={"example": True})
    is_verified: bool = Field(..., description="邮箱是否已验证", json_schema_extra={"example": False})
    created_at: datetime = Field(..., description="账户创建时间")

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    """Schema for updating user profile."""

    username: Optional[str] = Field(
        None,
        min_length=3,
        max_length=50,
        description="新用户名 (可选)",
        json_schema_extra={"example": "new_username"}
    )
    email: Optional[EmailStr] = Field(
        None,
        description="新邮箱地址 (可选)",
        json_schema_extra={"example": "new_email@example.com"}
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"username": "new_username"},
                {"email": "new_email@example.com"},
                {"username": "new_username", "email": "new_email@example.com"}
            ]
        }
    }

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        """Validate username format if provided."""
        if v is not None and not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Username can only contain letters, numbers, and underscores")
        return v


class PasswordChange(BaseModel):
    """Schema for password change."""

    current_password: str = Field(
        ...,
        description="当前密码",
        json_schema_extra={"example": "OldPass123"}
    )
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="新密码 (8-100 字符，必须包含大写字母、小写字母和数字)",
        json_schema_extra={"example": "NewSecurePass456"}
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "current_password": "OldPass123",
                    "new_password": "NewSecurePass456"
                }
            ]
        }
    }

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v
