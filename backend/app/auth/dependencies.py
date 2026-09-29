"""
MediStock Backend — Auth Dependencies

FastAPI dependencies for extracting the current user from JWT cookies
and enforcing role-based access control.
"""

from functools import wraps
from typing import Annotated

from fastapi import Cookie, Depends, Request
from sqlalchemy.orm import Session, joinedload

from app.common.exceptions import AuthenticationError, AuthorizationError
from app.core.security import decode_access_token
from app.db.session import get_db
from app.users.models import User


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    access_token: str | None = Cookie(default=None),
) -> User:
    """
    Extract and validate the JWT from the access_token cookie or Authorization header.
    Returns the current authenticated user or raises 401.
    """
    token = access_token
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()

    if not token:
        raise AuthenticationError("Not authenticated")

    payload = decode_access_token(token)
    if payload is None:
        raise AuthenticationError("Invalid or expired token")

    user_id = payload.get("sub")
    if user_id is None:
        raise AuthenticationError("Invalid token payload")

    user = (
        db.query(User)
        .options(joinedload(User.user_roles))
        .filter(User.id == int(user_id))
        .first()
    )
    if user is None:
        raise AuthenticationError("User not found")
    if not user.is_active:
        raise AuthenticationError("Account is deactivated")

    return user


# Type alias for dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*allowed_roles: str):
    """
    FastAPI dependency factory that checks if the current user has at
    least one of the specified roles.

    Usage:
        @router.get("/admin-only", dependencies=[Depends(require_roles("ADMIN"))])
    """

    def role_checker(current_user: CurrentUser) -> User:
        user_roles = set(current_user.roles)
        if not user_roles.intersection(allowed_roles):
            raise AuthorizationError(
                f"Requires one of: {', '.join(allowed_roles)}"
            )
        return current_user

    return Depends(role_checker)
