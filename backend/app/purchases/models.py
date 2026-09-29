"""
MediStock Backend — Purchase Models

SQLAlchemy ORM models for purchases and purchase items.
"""

from datetime import date, datetime, timezone

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Purchase(Base):
    """Purchase order header."""

    __tablename__ = "purchases"

    STATUSES = ("DRAFT", "ORDERED", "PARTIALLY_RECEIVED", "RECEIVED", "CANCELLED")

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    purchase_number: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    supplier_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("suppliers.id", ondelete="RESTRICT"), nullable=False
    )
    created_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    purchase_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="DRAFT")
    total_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    supplier: Mapped["app.suppliers.models.Supplier"] = relationship(
        back_populates="purchases"
    )
    creator: Mapped["app.users.models.User"] = relationship()
    items: Mapped[list["PurchaseItem"]] = relationship(
        back_populates="purchase", cascade="all, delete-orphan"
    )


class PurchaseItem(Base):
    """Line item within a purchase order."""

    __tablename__ = "purchase_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    purchase_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("purchases.id", ondelete="CASCADE"), nullable=False
    )
    medicine_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("medicines.id", ondelete="RESTRICT"), nullable=False
    )
    batch_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("batches.id", ondelete="SET NULL"), nullable=True
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_cost: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    total_cost: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    quantity_received: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Relationships
    purchase: Mapped["Purchase"] = relationship(back_populates="items")
    medicine: Mapped["app.medicines.models.Medicine"] = relationship()
    batch: Mapped["app.inventory.models.Batch | None"] = relationship()
