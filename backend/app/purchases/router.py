"""
MediStock Backend — Purchase Router
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import CurrentUser, require_roles
from app.common.pagination import paginate
from app.db.session import get_db
from app.purchases import repository, service
from app.purchases.schemas import PurchaseCreate, PurchaseReceiveRequest

router = APIRouter(prefix="/purchases", tags=["Purchases"])


@router.get("")
def list_purchases(
    page: int = 1,
    page_size: int = 20,
    supplier_id: int | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    query = repository.list_purchases_query(supplier_id=supplier_id, status=status)
    items, meta = paginate(db, query, page, page_size)
    return {
        "success": True,
        "data": {
            "items": [_resp(p, db) for p in items],
            "pagination": meta.model_dump(),
        },
    }


@router.post(
    "",
    status_code=201,
    dependencies=[require_roles("ADMIN", "INVENTORY_MANAGER")],
)
def create_purchase(
    body: PurchaseCreate,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    purchase = service.create_purchase(db, body, current_user.id)
    return {"success": True, "data": _resp(purchase, db), "message": "Purchase created"}


@router.get("/{purchase_id}")
def get_purchase(purchase_id: int, db: Session = Depends(get_db)):
    p = repository.get_purchase_by_id(db, purchase_id)
    if not p:
        from app.common.exceptions import NotFoundError
        raise NotFoundError("Purchase", purchase_id)
    return {"success": True, "data": _resp(p, db)}


@router.post(
    "/{purchase_id}/receive",
    dependencies=[require_roles("ADMIN", "INVENTORY_MANAGER")],
)
def receive_purchase(
    purchase_id: int,
    body: PurchaseReceiveRequest,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    purchase = service.receive_purchase(db, purchase_id, body, current_user.id)
    return {"success": True, "data": _resp(purchase, db), "message": "Purchase received"}


@router.patch(
    "/{purchase_id}/cancel",
    dependencies=[require_roles("ADMIN")],
)
def cancel_purchase(purchase_id: int, db: Session = Depends(get_db)):
    purchase = service.cancel_purchase(db, purchase_id)
    return {"success": True, "message": "Purchase cancelled"}


def _resp(p, db) -> dict:
    sup_name = None
    if hasattr(p, "supplier") and p.supplier:
        sup_name = p.supplier.name
    items = []
    if hasattr(p, "items"):
        for i in p.items:
            med_name = i.medicine.name if hasattr(i, "medicine") and i.medicine else None
            items.append({
                "id": i.id,
                "medicine_id": i.medicine_id,
                "medicine_name": med_name,
                "quantity": i.quantity,
                "unit_cost": float(i.unit_cost),
                "total_cost": float(i.total_cost),
                "quantity_received": i.quantity_received,
                "batch_id": i.batch_id,
            })
    return {
        "id": p.id,
        "purchase_number": p.purchase_number,
        "supplier_id": p.supplier_id,
        "supplier_name": sup_name,
        "created_by": p.created_by,
        "purchase_date": p.purchase_date.isoformat() if p.purchase_date else None,
        "status": p.status,
        "total_amount": float(p.total_amount),
        "notes": p.notes,
        "items": items,
        "created_at": p.created_at.isoformat() if p.created_at else None,
    }
