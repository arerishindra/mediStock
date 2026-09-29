"""
MediStock Backend — Alerts Router
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import CurrentUser, require_roles
from app.common.pagination import paginate
from app.db.session import get_db
from app.alerts import repository, service

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("")
def list_alerts(
    page: int = 1,
    page_size: int = 20,
    status: str | None = None,
    alert_type: str | None = None,
    db: Session = Depends(get_db),
):
    query = repository.list_alerts_query(status=status, alert_type=alert_type)
    items, meta = paginate(db, query, page, page_size)
    return {
        "success": True,
        "data": {
            "items": [_resp(a, db) for a in items],
            "pagination": meta.model_dump(),
        },
    }


@router.post(
    "/check",
    dependencies=[require_roles("ADMIN", "INVENTORY_MANAGER")],
)
def trigger_alert_check(db: Session = Depends(get_db)):
    """Trigger alert check for expiry and low-stock conditions."""
    result = service.check_alerts(db)
    return {"success": True, "data": result, "message": "Alert check completed"}


@router.patch("/{alert_id}/acknowledge")
def acknowledge_alert(
    alert_id: int,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    alert = service.acknowledge_alert(db, alert_id, current_user.id)
    return {"success": True, "data": _resp(alert, db), "message": "Alert acknowledged"}


def _resp(a, db) -> dict:
    med_name = None
    if hasattr(a, "medicine") and a.medicine:
        med_name = a.medicine.name
    return {
        "id": a.id,
        "alert_type": a.alert_type,
        "medicine_id": a.medicine_id,
        "medicine_name": med_name,
        "batch_id": a.batch_id,
        "message": a.message,
        "status": a.status,
        "acknowledged_by": a.acknowledged_by,
        "acknowledged_at": a.acknowledged_at.isoformat() if a.acknowledged_at else None,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    }
