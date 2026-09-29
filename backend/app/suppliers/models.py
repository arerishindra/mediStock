"""
MediStock Backend — Supplier Models

SQLAlchemy ORM models for suppliers and medicine-supplier links.
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Supplier(Base):
    """Pharmaceutical supplier / distributor."""

    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    contact_person: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    tax_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    payment_terms: Mapped[str | None] = mapped_column(String(100), nullable=True)
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
    medicine_suppliers: Mapped[list["MedicineSupplier"]] = relationship(
        back_populates="supplier"
    )
    purchases: Mapped[list["app.purchases.models.Purchase"]] = relationship(
        back_populates="supplier"
    )


class MedicineSupplier(Base):
    """Many-to-many link between medicines and suppliers."""

    __tablename__ = "medicine_suppliers"
    __table_args__ = (
        UniqueConstraint("medicine_id", "supplier_id", name="uq_medicine_supplier"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    medicine_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("medicines.id", ondelete="CASCADE"), nullable=False
    )
    supplier_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False
    )

    # Relationships
    medicine: Mapped["app.medicines.models.Medicine"] = relationship(
        back_populates="medicine_suppliers"
    )
    supplier: Mapped["Supplier"] = relationship(back_populates="medicine_suppliers")
