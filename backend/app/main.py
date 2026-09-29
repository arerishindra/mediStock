"""
MediStock Backend — FastAPI Application

Main application factory with middleware, exception handlers, and router registration.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.common.exceptions import (
    AuthenticationError,
    AuthorizationError,
    BusinessRuleError,
    DuplicateError,
    MediStockError,
    NotFoundError,
)
from app.core.config import settings
from app.db.base import Base
from app.db.session import SessionLocal, engine

# Import models so Base.metadata contains all tables
import app.users.models  # noqa: F401
import app.medicines.models  # noqa: F401
import app.suppliers.models  # noqa: F401
import app.inventory.models  # noqa: F401
import app.purchases.models  # noqa: F401
import app.sales.models  # noqa: F401
import app.returns.models  # noqa: F401
import app.alerts.models  # noqa: F401
import app.common.audit  # noqa: F401


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Application startup/shutdown lifecycle."""
    # Create tables (for SQLite dev mode — production uses Alembic)
    Base.metadata.create_all(bind=engine)

    # Run seed data
    from app.db.seed import run_seed

    db = SessionLocal()
    try:
        run_seed(db)
    finally:
        db.close()

    yield  # Application runs here

    # Shutdown (cleanup if needed)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Pharmacy Inventory and Operations Management API",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    # --- Middleware ---

    application.add_middleware(
        CORSMiddleware,
        allow_origins=[
            settings.FRONTEND_URL,
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3001",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    # --- Exception Handlers ---

    @application.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "error": {"code": exc.code, "message": exc.message},
            },
        )

    @application.exception_handler(DuplicateError)
    async def duplicate_handler(request: Request, exc: DuplicateError):
        return JSONResponse(
            status_code=409,
            content={
                "success": False,
                "error": {"code": exc.code, "message": exc.message},
            },
        )

    @application.exception_handler(AuthenticationError)
    async def auth_error_handler(request: Request, exc: AuthenticationError):
        return JSONResponse(
            status_code=401,
            content={
                "success": False,
                "error": {"code": exc.code, "message": exc.message},
            },
        )

    @application.exception_handler(AuthorizationError)
    async def authz_error_handler(request: Request, exc: AuthorizationError):
        return JSONResponse(
            status_code=403,
            content={
                "success": False,
                "error": {"code": exc.code, "message": exc.message},
            },
        )

    @application.exception_handler(BusinessRuleError)
    async def business_rule_handler(request: Request, exc: BusinessRuleError):
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": {"code": exc.code, "message": exc.message},
            },
        )

    @application.exception_handler(MediStockError)
    async def medistock_error_handler(request: Request, exc: MediStockError):
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {"code": exc.code, "message": exc.message},
            },
        )

    # --- Routes ---

    @application.get("/api/v1/health", tags=["Health"])
    async def health_check():
        """Health check endpoint — no authentication required."""
        return {
            "success": True,
            "data": {
                "status": "healthy",
                "version": settings.APP_VERSION,
                "app": settings.APP_NAME,
            },
        }

    # --- Register Module Routers ---
    from app.auth.router import router as auth_router
    from app.users.router import router as users_router
    from app.medicines.router import router as medicines_router
    from app.suppliers.router import router as suppliers_router
    from app.inventory.router import router as inventory_router
    from app.purchases.router import router as purchases_router
    from app.sales.router import router as sales_router
    from app.returns.router import router as returns_router
    from app.alerts.router import router as alerts_router
    from app.reports.router import router as reports_router

    application.include_router(auth_router, prefix="/api/v1")
    application.include_router(users_router, prefix="/api/v1")
    application.include_router(medicines_router, prefix="/api/v1")
    application.include_router(suppliers_router, prefix="/api/v1")
    application.include_router(inventory_router, prefix="/api/v1")
    application.include_router(purchases_router, prefix="/api/v1")
    application.include_router(sales_router, prefix="/api/v1")
    application.include_router(returns_router, prefix="/api/v1")
    application.include_router(alerts_router, prefix="/api/v1")
    application.include_router(reports_router, prefix="/api/v1")

    return application


app = create_app()
