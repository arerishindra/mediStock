"""
MediStock Backend — User Repository

Database queries for user operations.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.users.models import Role, User, UserRole


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """Fetch a user by ID with roles eagerly loaded."""
    return (
        db.query(User)
        .options(joinedload(User.user_roles).joinedload(UserRole.role))
        .filter(User.id == user_id)
        .first()
    )


def get_user_by_email(db: Session, email: str) -> User | None:
    """Fetch a user by email."""
    return db.query(User).filter(User.email == email).first()


def list_users(db: Session, page: int = 1, page_size: int = 20):
    """Return a paginated query of all users."""
    query = (
        select(User)
        .options(joinedload(User.user_roles).joinedload(UserRole.role))
        .order_by(User.id)
    )
    return query


def get_roles_by_names(db: Session, role_names: list[str]) -> list[Role]:
    """Fetch roles by their names."""
    return db.query(Role).filter(Role.name.in_(role_names)).all()


def get_all_roles(db: Session) -> list[Role]:
    """Fetch all available roles."""
    return db.query(Role).all()
