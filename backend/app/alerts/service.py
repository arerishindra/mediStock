"""
MediStock Backend — Alerts Service

Generates expiry and low-stock alerts with deduplication.
"""

from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.alerts.models import Alert
from app.alerts.repository import find_active_alert
from app.inventory.models import Batch
from app.medicines.models import Medicine


def check_alerts(db: Session, expiry_days: int = 90) -> dict:
    """
    Run alert checks for:
    1. Medicines expiring within `expiry_days`
    2. Medicines below reorder level
    Returns count of new alerts created.
    """
    expiry_count = _check_expiry_alerts(db, expiry_days)
    low_stock_count = _check_low_stock_alerts(db)
    db.commit()
    return {"expiry_alerts": expiry_count, "low_stock_alerts": low_stock_count}


def acknowledge_alert(db: Session, alert_id: int, user_id: int) -> Alert:
    """Acknowledge an active alert."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        from app.common.exceptions import NotFoundError
        raise NotFoundError("Alert", alert_id)

    alert.status = "ACKNOWLEDGED"
    alert.acknowledged_by = user_id
    alert.acknowledged_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(alert)
    return alert


def _check_expiry_alerts(db: Session, expiry_days: int) -> int:
    """Create alerts for batches expiring within the given window."""
    threshold = date.today() + timedelta(days=expiry_days)
    batches = (
        db.query(Batch)
        .filter(
            Batch.is_active == True,
            Batch.current_quantity > 0,
            Batch.expiry_date <= threshold,
        )
        .all()
    )

    count = 0
    for batch in batches:
        existing = find_active_alert(db, "EXPIRY", batch.medicine_id, batch.id)
        if existing:
            continue

        days_left = (batch.expiry_date - date.today()).days
        if days_left < 0:
            message = f"Batch {batch.batch_number} has EXPIRED ({batch.expiry_date})"
        else:
            message = f"Batch {batch.batch_number} expires in {days_left} days ({batch.expiry_date})"

        alert = Alert(
            alert_type="EXPIRY",
            medicine_id=batch.medicine_id,
            batch_id=batch.id,
            message=message,
        )
        db.add(alert)
        count += 1

    return count


def _check_low_stock_alerts(db: Session) -> int:
    """Create alerts for medicines below reorder level."""
    # Get total stock per medicine
    stock_data = (
        db.query(
            Medicine.id,
            Medicine.name,
            Medicine.reorder_level,
            func.coalesce(func.sum(Batch.current_quantity), 0).label("total_stock"),
        )
        .outerjoin(Batch, (Batch.medicine_id == Medicine.id) & (Batch.is_active == True))
        .filter(Medicine.is_active == True)
        .group_by(Medicine.id)
        .all()
    )

    count = 0
    for med_id, med_name, reorder_level, total_stock in stock_data:
        if total_stock >= reorder_level:
            # Resolve any existing alert
            existing = find_active_alert(db, "LOW_STOCK", med_id)
            if existing:
                existing.status = "RESOLVED"
            continue

        existing = find_active_alert(db, "LOW_STOCK", med_id)
        if existing:
            continue

        alert = Alert(
            alert_type="LOW_STOCK",
            medicine_id=med_id,
            message=f"{med_name} stock ({total_stock}) is below reorder level ({reorder_level})",
        )
        db.add(alert)
        count += 1

    return count
