"""
MediStock Backend — Inventory Models

SQLAlchemy ORM models for batches and stock movements.
"""

from datetime import date, datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    Boolean,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Batch(Base):
    """Individual stock batch for a medicine from a specific supplier."""

    __tablename__ = "batches"
    __table_args__ = (
        UniqueConstraint("medicine_id", "batch_number", name="uq_medicine_batch"),
        CheckConstraint("current_quantity >= 0", name="ck_batch_qty_nonneg"),
        Index("ix_batch_expiry", "expiry_date"),
        Index("ix_batch_stock", "medicine_id", "current_quantity"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    medicine_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("medicines.id", ondelete="RESTRICT"), nullable=False
    )
    supplier_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("suppliers.id", ondelete="SET NULL"), nullable=True
    )
    batch_number: Mapped[str] = mapped_column(String(100), nullable=False)
    manufacturing_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[date] = mapped_column(Date, nullable=False)
    quantity_received: Mapped[int] = mapped_column(Integer, nullable=False)
    current_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    cost_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    selling_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
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
    medicine: Mapped["app.medicines.models.Medicine"] = relationship(
        back_populates="batches"
    )
    supplier: Mapped["app.suppliers.models.Supplier | None"] = relationship()
    stock_movements: Mapped[list["StockMovement"]] = relationship(
        back_populates="batch", order_by="StockMovement.created_at"
    )


class StockMovement(Base):
    """Immutable ledger entry for every stock change."""

    __tablename__ = "stock_movements"
    __table_args__ = (
        Index("ix_sm_batch_created", "batch_id", "created_at"),
        Index("ix_sm_reference", "reference_type", "reference_id"),
        Index("ix_sm_performed_by", "performed_by"),
    )

    MOVEMENT_TYPES = (
        "PURCHASE_RECEIPT",
        "SALE",
        "CUSTOMER_RETURN",
        "SUPPLIER_RETURN",
        "ADJUSTMENT_IN",
        "ADJUSTMENT_OUT",
        "WRITE_OFF",
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    batch_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("batches.id", ondelete="RESTRICT"), nullable=False
    )
    movement_type: Mapped[str] = mapped_column(String(30), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)  # signed: + in, - out
    quantity_after: Mapped[int] = mapped_column(Integer, nullable=False)
    reference_type: Mapped[str] = mapped_column(String(50), nullable=False)
    reference_id: Mapped[int] = mapped_column(Integer, nullable=False)
    performed_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    batch: Mapped["Batch"] = relationship(back_populates="stock_movements")
    user: Mapped["app.users.models.User"] = relationship()
