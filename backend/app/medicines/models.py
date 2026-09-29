"""
MediStock Backend — Medicine & Category Models

SQLAlchemy ORM models for medicines and categories.
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from app.db.base import Base


class Category(Base):
    """Medicine category (e.g., Tablets, Syrups, Injectables)."""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    medicines: Mapped[list["Medicine"]] = relationship(back_populates="category")


class Medicine(Base):
    """Medicine in the pharmacy catalog."""

    __tablename__ = "medicines"
    __table_args__ = (
        UniqueConstraint("name", "strength", "dosage_form", name="uq_medicine_identity"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    generic_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False
    )
    manufacturer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    dosage_form: Mapped[str] = mapped_column(String(50), nullable=False)
    strength: Mapped[str] = mapped_column(String(50), nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    reorder_level: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
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
    category: Mapped["Category"] = relationship(back_populates="medicines")
    batches: Mapped[list["app.inventory.models.Batch"]] = relationship(
        back_populates="medicine", foreign_keys="Batch.medicine_id"
    )
    medicine_suppliers: Mapped[list["app.suppliers.models.MedicineSupplier"]] = relationship(
        back_populates="medicine"
    )
