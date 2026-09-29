"""
MediStock Backend — Declarative Base

All SQLAlchemy models inherit from this Base.
Import all models here so Alembic can discover them.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    pass


# Import all models below so they register with Base.metadata.
# This is required for Alembic autogenerate to detect them.
from app.users.models import User, Role, UserRole  # noqa: E402, F401
from app.medicines.models import Category, Medicine  # noqa: E402, F401
from app.suppliers.models import Supplier, MedicineSupplier  # noqa: E402, F401
from app.inventory.models import Batch, StockMovement  # noqa: E402, F401
from app.purchases.models import Purchase, PurchaseItem  # noqa: E402, F401
from app.sales.models import Sale, SaleItem  # noqa: E402, F401
from app.returns.models import Return, ReturnItem  # noqa: E402, F401
from app.alerts.models import Alert  # noqa: E402, F401
from app.common.audit import AuditLog  # noqa: E402, F401
