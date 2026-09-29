"""
MediStock Backend — Auth Router

Endpoints: POST /auth/login, POST /auth/logout, GET /auth/me
"""

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.auth.dependencies import CurrentUser
from app.auth.schemas import LoginRequest, UserProfile
from app.auth.service import authenticate_user, create_user_token
from app.core.config import settings
from app.db.session import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login")
def login(body: LoginRequest, response: Response, db: Session = Depends(get_db)):
    """Authenticate user and set JWT cookie."""
    user = authenticate_user(db, body.email, body.password)
    token = create_user_token(user)

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )

    return {
        "success": True,
        "data": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "roles": user.roles,
            "access_token": token,
        },
        "message": "Login successful",
    }


@router.post("/logout")
def logout(response: Response, current_user: CurrentUser):
    """Clear the authentication cookie."""
    response.delete_cookie(key="access_token", path="/")
    return {"success": True, "message": "Logged out successfully"}


@router.get("/me", response_model=None)
def get_me(current_user: CurrentUser):
    """Get the current authenticated user's profile."""
    return {
        "success": True,
        "data": {
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "roles": current_user.roles,
            "is_active": current_user.is_active,
        },
    }
