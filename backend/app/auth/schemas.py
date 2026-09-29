"""
MediStock Backend — Auth Schemas

Pydantic schemas for authentication requests and responses.
"""

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Login request body."""

    email: str
    password: str


class TokenData(BaseModel):
    """Data extracted from a JWT token."""

    user_id: int
    email: str
    roles: list[str]


class UserProfile(BaseModel):
    """Current user profile returned by /auth/me."""

    id: int
    email: str
    full_name: str
    roles: list[str]
    is_active: bool

    model_config = {"from_attributes": True}
