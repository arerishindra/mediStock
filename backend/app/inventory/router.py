"""
MediStock Backend — Inventory Router
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import CurrentUser, require_roles
from app.common.pagination import paginate
from app.db.session import get_db
from app.inventory import repository, service
from app.inventory.schemas import StockAdjustmentRequest

router = APIRouter(tags=["Inventory"])


@router.get("/inventory")
def inventory_summary(db: Session = Depends(get_db)):
    """Get inventory summary grouped by medicine."""
    results = repository.get_inventory_summary(db)
    items = [
        {
            "medicine_id": r[0],
            "medicine_name": r[1],
            "total_quantity": int(r[2]) if r[2] else 0,
            "batch_count": int(r[3]) if r[3] else 0,
            "total_value": float(r[4]) if r[4] else 0.0,
        }
        for r in results
    ]
    return {"success": True, "data": {"items": items}}


@router.get("/inventory/{medicine_id}/batches")
def list_batches(medicine_id: int, db: Session = Depends(get_db)):
    """List all batches for a specific medicine."""
    query = repository.list_batches_for_medicine(db, medicine_id)
    items, meta = paginate(db, query, page=1, page_size=100)
    return {
        "success": True,
        "data": {
            "items": [_batch_resp(b) for b in items],
            "pagination": meta.model_dump(),
        },
    }


@router.get("/batches/{batch_id}")
def get_batch(batch_id: int, db: Session = Depends(get_db)):
    """Get a specific batch by ID."""
    batch = repository.get_batch_by_id(db, batch_id)
    if not batch:
        from app.common.exceptions import NotFoundError
        raise NotFoundError("Batch", batch_id)
    return {"success": True, "data": _batch_resp(batch)}


@router.post(
    "/inventory/adjustments",
    status_code=201,
    dependencies=[require_roles("ADMIN", "INVENTORY_MANAGER")],
)
def create_adjustment(
    body: StockAdjustmentRequest,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    """Create a stock adjustment."""
    movement = service.create_stock_adjustment(db, body, current_user.id)
    return {
        "success": True,
        "data": _movement_resp(movement),
        "message": "Stock adjustment recorded",
    }


@router.get("/stock-movements")
def list_movements(
    page: int = 1,
    page_size: int = 20,
    batch_id: int | None = None,
    movement_type: str | None = None,
    medicine_id: int | None = None,
    db: Session = Depends(get_db),
):
    """List stock movements with filtering."""
    query = repository.list_stock_movements_query(
        batch_id=batch_id,
        movement_type=movement_type,
        medicine_id=medicine_id,
    )
    items, meta = paginate(db, query, page, page_size)
    return {
        "success": True,
        "data": {
            "items": [_movement_resp(m) for m in items],
            "pagination": meta.model_dump(),
        },
    }


def _batch_resp(b) -> dict:
    med_name = None
    if hasattr(b, "medicine") and b.medicine:
        med_name = b.medicine.name
    return {
        "id": b.id,
        "medicine_id": b.medicine_id,
        "medicine_name": med_name,
        "supplier_id": b.supplier_id,
        "batch_number": b.batch_number,
        "manufacturing_date": b.manufacturing_date.isoformat() if b.manufacturing_date else None,
        "expiry_date": b.expiry_date.isoformat() if b.expiry_date else None,
        "quantity_received": b.quantity_received,
        "current_quantity": b.current_quantity,
        "cost_price": float(b.cost_price),
        "selling_price": float(b.selling_price),
        "is_active": b.is_active,
        "created_at": b.created_at.isoformat() if b.created_at else None,
    }


def _movement_resp(m) -> dict:
    return {
        "id": m.id,
        "batch_id": m.batch_id,
        "movement_type": m.movement_type,
        "quantity": m.quantity,
        "quantity_after": m.quantity_after,
        "reference_type": m.reference_type,
        "reference_id": m.reference_id,
        "performed_by": m.performed_by,
        "notes": m.notes,
        "created_at": m.created_at.isoformat() if m.created_at else None,
    }
