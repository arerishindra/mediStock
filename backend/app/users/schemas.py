"""
MediStock Backend — User Schemas

Pydantic schemas for user CRUD operations.
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Schema for creating a new user."""

    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
    role_names: list[str] = Field(default_factory=list)


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    full_name: str | None = Field(None, min_length=1, max_length=255)
    email: EmailStr | None = None
    is_active: bool | None = None


class UserRolesUpdate(BaseModel):
    """Schema for updating user roles."""

    role_names: list[str]


class PasswordChange(BaseModel):
    """Schema for changing password."""

    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


class UserResponse(BaseModel):
    """Schema for user in API responses."""

    id: int
    email: str
    full_name: str
    is_active: bool
    roles: list[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
