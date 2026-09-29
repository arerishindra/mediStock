"""
MediStock Backend — Alert Models

SQLAlchemy ORM models for expiry and low-stock alerts.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Alert(Base):
    """System alert for expiry or low-stock conditions."""

    __tablename__ = "alerts"
    __table_args__ = (
        # Only one ACTIVE alert per (type, medicine, batch) combination
        Index("ix_alert_dedup", "alert_type", "medicine_id", "batch_id"),
    )

    ALERT_TYPES = ("EXPIRY", "LOW_STOCK")
    STATUSES = ("ACTIVE", "ACKNOWLEDGED", "RESOLVED")

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    alert_type: Mapped[str] = mapped_column(String(20), nullable=False)
    medicine_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("medicines.id", ondelete="CASCADE"), nullable=False
    )
    batch_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("batches.id", ondelete="CASCADE"), nullable=True
    )
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")
    acknowledged_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    medicine: Mapped["app.medicines.models.Medicine"] = relationship()
    batch: Mapped["app.inventory.models.Batch | None"] = relationship()
    acknowledger: Mapped["app.users.models.User | None"] = relationship()
