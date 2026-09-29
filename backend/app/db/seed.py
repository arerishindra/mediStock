"""
MediStock Backend — Database Seed Data

Creates initial roles and the default admin user on first run.
"""

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.users.models import Role, User, UserRole


ROLES = [
    {"name": "ADMIN", "description": "Full system access"},
    {"name": "PHARMACIST", "description": "Sales, returns, and read access"},
    {"name": "INVENTORY_MANAGER", "description": "Inventory, purchases, suppliers"},
    {"name": "AUDITOR", "description": "Read-only access to logs and reports"},
]

DEFAULT_ADMIN = {
    "email": "admin@medistock.local",
    "full_name": "System Administrator",
    "password": "Admin@123",  # Change immediately after first login
}


def seed_roles(db: Session) -> list[Role]:
    """Create predefined roles if they do not exist."""
    created = []
    for role_data in ROLES:
        existing = db.query(Role).filter(Role.name == role_data["name"]).first()
        if not existing:
            role = Role(**role_data)
            db.add(role)
            created.append(role)
    if created:
        db.commit()
    return created


def seed_admin(db: Session) -> User | None:
    """Create the default admin user if no admin exists."""
    existing = db.query(User).filter(User.email == DEFAULT_ADMIN["email"]).first()
    if existing:
        return None

    admin_role = db.query(Role).filter(Role.name == "ADMIN").first()
    if not admin_role:
        return None

    admin = User(
        email=DEFAULT_ADMIN["email"],
        full_name=DEFAULT_ADMIN["full_name"],
        password_hash=hash_password(DEFAULT_ADMIN["password"]),
    )
    db.add(admin)
    db.flush()

    user_role = UserRole(user_id=admin.id, role_id=admin_role.id)
    db.add(user_role)
    db.commit()

    return admin


def run_seed(db: Session) -> None:
    """Run all seed operations."""
    seed_roles(db)
    seed_admin(db)
