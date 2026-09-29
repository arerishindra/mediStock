"""
MediStock Backend — Sales Models

SQLAlchemy ORM models for sales and sale items.
"""

from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Sale(Base):
    """Sale / invoice header."""

    __tablename__ = "sales"

    STATUSES = ("COMPLETED", "RETURNED")

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    invoice_number: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    sold_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    customer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    customer_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    sale_date: Mapped[date] = mapped_column(Date, nullable=False)
    subtotal: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    discount_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    tax_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    total_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    payment_method: Mapped[str] = mapped_column(String(30), nullable=False, default="CASH")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="COMPLETED")
    idempotency_key: Mapped[str | None] = mapped_column(
        String(100), unique=True, nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    seller: Mapped["app.users.models.User"] = relationship()
    items: Mapped[list["SaleItem"]] = relationship(
        back_populates="sale", cascade="all, delete-orphan"
    )


class SaleItem(Base):
    """Line item within a sale."""

    __tablename__ = "sale_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sale_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sales.id", ondelete="CASCADE"), nullable=False
    )
    medicine_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("medicines.id", ondelete="RESTRICT"), nullable=False
    )
    batch_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("batches.id", ondelete="RESTRICT"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    total_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    # Relationships
    sale: Mapped["Sale"] = relationship(back_populates="items")
    medicine: Mapped["app.medicines.models.Medicine"] = relationship()
    batch: Mapped["app.inventory.models.Batch"] = relationship()
