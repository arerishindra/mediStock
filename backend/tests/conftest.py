"""
MediStock Backend — Test Configuration & Fixtures

Sets up an isolated SQLite in-memory database and test client for each test session.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.core.security import create_access_token, hash_password
from app.db.base import Base
import app.db.session as db_session_module
from app.db.session import get_db
from app.main import create_app
from app.users.models import Role, User, UserRole

# Use SQLite in-memory with StaticPool so all connections share the same in-memory DB
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Monkeypatch session module engine and SessionLocal for tests
db_session_module.engine = engine
db_session_module.SessionLocal = TestingSessionLocal


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test function."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    # Seed roles
    roles = [
        Role(name="ADMIN", description="Full system access"),
        Role(name="PHARMACIST", description="Sales, returns, read"),
        Role(name="INVENTORY_MANAGER", description="Inventory, purchases"),
        Role(name="AUDITOR", description="Read-only"),
    ]
    for r in roles:
        existing = session.query(Role).filter_by(name=r.name).first()
        if not existing:
            session.add(r)
    session.commit()

    # Seed test admin user
    existing_admin = session.query(User).filter_by(email="admin@test.com").first()
    if not existing_admin:
        admin = User(
            email="admin@test.com",
            full_name="Admin Test",
            password_hash=hash_password("Admin@123"),
            is_active=True,
        )
        session.add(admin)
        session.commit()

        admin_role = session.query(Role).filter_by(name="ADMIN").first()
        session.add(UserRole(user_id=admin.id, role_id=admin_role.id))
        session.commit()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """TestClient that overrides get_db dependency to use the isolated test database."""
    app = create_app()

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c


@pytest.fixture
def admin_headers(db_session):
    """Headers containing valid JWT auth token for the test admin user."""
    admin = db_session.query(User).filter_by(email="admin@test.com").first()
    token = create_access_token({"sub": str(admin.id), "email": admin.email, "roles": ["ADMIN"]})
    return {"Authorization": f"Bearer {token}"}
