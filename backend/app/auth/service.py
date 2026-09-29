"""
MediStock Backend — Auth Service

Handles authentication logic: credential verification and token creation.
"""

from sqlalchemy.orm import Session, joinedload

from app.common.exceptions import AuthenticationError
from app.core.security import create_access_token, verify_password
from app.users.models import User


def authenticate_user(db: Session, email: str, password: str) -> User:
    """Verify email + password. Returns user or raises AuthenticationError."""
    user = (
        db.query(User)
        .options(joinedload(User.user_roles))
        .filter(User.email == email)
        .first()
    )
    if not user or not verify_password(password, user.password_hash):
        raise AuthenticationError("Invalid email or password")
    if not user.is_active:
        raise AuthenticationError("Account is deactivated")
    return user


def create_user_token(user: User) -> str:
    """Create a JWT token with user ID, email, and roles."""
    return create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "roles": user.roles,
        }
    )
