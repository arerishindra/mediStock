"""
MediStock Backend — User Router

Endpoints for user management (ADMIN only).
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import CurrentUser, require_roles
from app.common.pagination import paginate
from app.db.session import get_db
from app.users import repository, service
from app.users.schemas import UserCreate, UserResponse, UserRolesUpdate, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", dependencies=[require_roles("ADMIN")])
def list_users(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    """List all users (paginated). ADMIN only."""
    query = repository.list_users(db)
    items, meta = paginate(db, query, page, page_size)
    return {
        "success": True,
        "data": {
            "items": [_to_response(u) for u in items],
            "pagination": meta.model_dump(),
        },
    }


@router.post("", status_code=201, dependencies=[require_roles("ADMIN")])
def create_user(body: UserCreate, db: Session = Depends(get_db)):
    """Create a new user. ADMIN only."""
    user = service.create_user(db, body)
    return {
        "success": True,
        "data": _to_response(user),
        "message": "User created successfully",
    }


@router.get("/{user_id}", dependencies=[require_roles("ADMIN")])
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a user by ID. ADMIN only."""
    user = repository.get_user_by_id(db, user_id)
    if not user:
        from app.common.exceptions import NotFoundError

        raise NotFoundError("User", user_id)
    return {"success": True, "data": _to_response(user)}


@router.put("/{user_id}", dependencies=[require_roles("ADMIN")])
def update_user(user_id: int, body: UserUpdate, db: Session = Depends(get_db)):
    """Update a user. ADMIN only."""
    user = service.update_user(db, user_id, body)
    return {"success": True, "data": _to_response(user), "message": "User updated"}


@router.patch("/{user_id}/roles", dependencies=[require_roles("ADMIN")])
def update_roles(user_id: int, body: UserRolesUpdate, db: Session = Depends(get_db)):
    """Update user roles. ADMIN only."""
    user = service.update_user_roles(db, user_id, body.role_names)
    return {"success": True, "data": _to_response(user), "message": "Roles updated"}


@router.delete("/{user_id}", dependencies=[require_roles("ADMIN")])
def deactivate_user(user_id: int, db: Session = Depends(get_db)):
    """Deactivate a user (soft delete). ADMIN only."""
    user = service.deactivate_user(db, user_id)
    return {"success": True, "message": "User deactivated"}


def _to_response(user) -> dict:
    """Convert a User model to a response dict."""
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "roles": user.roles,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
    }
