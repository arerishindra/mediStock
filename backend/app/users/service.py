"""
MediStock Backend — User Service

Business logic for user management.
"""

from sqlalchemy.orm import Session

from app.common.exceptions import DuplicateError, NotFoundError
from app.core.security import hash_password
from app.users.models import User, UserRole
from app.users.repository import get_roles_by_names, get_user_by_email, get_user_by_id
from app.users.schemas import UserCreate, UserUpdate


def create_user(db: Session, data: UserCreate) -> User:
    """Create a new user with the given roles."""
    # Check for duplicate email
    if get_user_by_email(db, data.email):
        raise DuplicateError("User", "email", data.email)

    user = User(
        email=data.email,
        full_name=data.full_name,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    db.flush()

    # Assign roles
    if data.role_names:
        roles = get_roles_by_names(db, data.role_names)
        for role in roles:
            db.add(UserRole(user_id=user.id, role_id=role.id))

    db.commit()
    db.refresh(user)
    return get_user_by_id(db, user.id)


def update_user(db: Session, user_id: int, data: UserUpdate) -> User:
    """Update user fields."""
    user = get_user_by_id(db, user_id)
    if not user:
        raise NotFoundError("User", user_id)

    if data.email and data.email != user.email:
        existing = get_user_by_email(db, data.email)
        if existing:
            raise DuplicateError("User", "email", data.email)
        user.email = data.email

    if data.full_name is not None:
        user.full_name = data.full_name
    if data.is_active is not None:
        user.is_active = data.is_active

    db.commit()
    db.refresh(user)
    return user


def update_user_roles(db: Session, user_id: int, role_names: list[str]) -> User:
    """Replace user roles."""
    user = get_user_by_id(db, user_id)
    if not user:
        raise NotFoundError("User", user_id)

    # Clear existing roles
    for ur in user.user_roles:
        db.delete(ur)
    db.flush()

    # Assign new roles
    roles = get_roles_by_names(db, role_names)
    for role in roles:
        db.add(UserRole(user_id=user.id, role_id=role.id))

    db.commit()
    return get_user_by_id(db, user_id)


def deactivate_user(db: Session, user_id: int) -> User:
    """Soft-delete a user by setting is_active to False."""
    user = get_user_by_id(db, user_id)
    if not user:
        raise NotFoundError("User", user_id)

    user.is_active = False
    db.commit()
    return user
