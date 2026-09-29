"""
MediStock Backend — Alerts Repository
"""

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.alerts.models import Alert


def get_alert_by_id(db: Session, alert_id: int) -> Alert | None:
    return (
        db.query(Alert)
        .options(joinedload(Alert.medicine))
        .filter(Alert.id == alert_id)
        .first()
    )


def list_alerts_query(status: str | None = None, alert_type: str | None = None):
    query = select(Alert).order_by(Alert.created_at.desc())
    if status:
        query = query.where(Alert.status == status)
    if alert_type:
        query = query.where(Alert.alert_type == alert_type)
    return query


def find_active_alert(
    db: Session,
    alert_type: str,
    medicine_id: int,
    batch_id: int | None = None,
) -> Alert | None:
    """Check for existing active alert for deduplication."""
    query = db.query(Alert).filter(
        Alert.alert_type == alert_type,
        Alert.medicine_id == medicine_id,
        Alert.status == "ACTIVE",
    )
    if batch_id:
        query = query.filter(Alert.batch_id == batch_id)
    return query.first()
