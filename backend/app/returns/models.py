"""
MediStock Backend — Return Models

SQLAlchemy ORM models for customer and supplier returns.
"""

from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Return(Base):
    """Return header (customer or supplier)."""

    __tablename__ = "returns"

    TYPES = ("CUSTOMER", "SUPPLIER")
    STATUSES = ("PENDING_INSPECTION", "PROCESSED", "CANCELLED")

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    return_number: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    return_type: Mapped[str] = mapped_column(String(20), nullable=False)
    sale_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("sales.id", ondelete="RESTRICT"), nullable=True
    )
    purchase_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("purchases.id", ondelete="RESTRICT"), nullable=True
    )
    processed_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    return_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="PENDING_INSPECTION"
    )
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
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
    processor: Mapped["app.users.models.User"] = relationship()
    sale: Mapped["app.sales.models.Sale | None"] = relationship()
    purchase: Mapped["app.purchases.models.Purchase | None"] = relationship()
    items: Mapped[list["ReturnItem"]] = relationship(
        back_populates="return_record", cascade="all, delete-orphan"
    )


class ReturnItem(Base):
    """Line item within a return."""

    __tablename__ = "return_items"

    CONDITION_STATUSES = ("RESTOCKED", "QUARANTINED", "WRITTEN_OFF")

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    return_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("returns.id", ondelete="CASCADE"), nullable=False
    )
    medicine_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("medicines.id", ondelete="RESTRICT"), nullable=False
    )
    batch_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("batches.id", ondelete="RESTRICT"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    total_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    condition_status: Mapped[str] = mapped_column(String(30), nullable=False, default="RESTOCKED")

    # Relationships
    return_record: Mapped["Return"] = relationship(back_populates="items")
    medicine: Mapped["app.medicines.models.Medicine"] = relationship()
    batch: Mapped["app.inventory.models.Batch"] = relationship()
