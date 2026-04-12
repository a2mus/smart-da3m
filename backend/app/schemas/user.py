"""
Pydantic schemas for authentication and user management.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.user import Language, UserRole


# Token schemas
class Token(BaseModel):
    """Token response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """JWT token payload schema."""

    sub: Optional[str] = None
    exp: Optional[int] = None
    type: Optional[str] = None
    role: Optional[str] = None
    language: Optional[str] = None


class RefreshRequest(BaseModel):
    """Refresh token request schema."""

    refresh_token: str


# Base user schemas
class UserBase(BaseModel):
    """Base user schema with common attributes."""

    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    language: Language = Language.AR


class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: Optional[str] = Field(None, min_length=8)
    pin_code: Optional[str] = Field(None, min_length=4, max_length=6)
    parent_id: Optional[UUID] = None


class UserResponse(UserBase):
    """Schema for user responses."""

    id: UUID
    parent_id: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Login schemas
class LoginRequest(BaseModel):
    """Email/password login request."""

    email: EmailStr
    password: str = Field(..., min_length=8)


class StudentPinLogin(BaseModel):
    """Student PIN login request."""

    pin_code: str = Field(..., min_length=4, max_length=6)

    @field_validator("pin_code")
    @classmethod
    def validate_pin_is_numeric(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError("PIN code must contain only digits")
        return v


# Registration schemas
class ParentRegisterRequest(BaseModel):
    """Parent registration request."""

    email: EmailStr
    password: str = Field(..., min_length=8)
    language: str = Field(default="AR", pattern="^(AR|FR)$")


class StudentCreate(BaseModel):
    """Student creation request (by parent)."""

    parent_id: UUID
    pin_code: str = Field(..., min_length=4, max_length=6)

    @field_validator("pin_code")
    @classmethod
    def validate_pin_is_numeric(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError("PIN code must contain only digits")
        return v
