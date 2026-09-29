"""
MediStock Backend — Returns Router
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import CurrentUser, require_roles
from app.common.pagination import paginate
from app.db.session import get_db
from app.returns import repository, service
from app.returns.schemas import CustomerReturnCreate, SupplierReturnCreate

router = APIRouter(prefix="/returns", tags=["Returns"])


@router.get("")
def list_returns(
    page: int = 1,
    page_size: int = 20,
    return_type: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    query = repository.list_returns_query(return_type=return_type, status=status)
    items, meta = paginate(db, query, page, page_size)
    return {
        "success": True,
        "data": {
            "items": [_resp(r) for r in items],
            "pagination": meta.model_dump(),
        },
    }


@router.post(
    "/customer",
    status_code=201,
    dependencies=[require_roles("ADMIN", "PHARMACIST", "INVENTORY_MANAGER")],
)
def create_customer_return(
    body: CustomerReturnCreate,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    ret = service.create_customer_return(db, body, current_user.id)
    return {"success": True, "data": _resp(ret), "message": "Customer return created"}


@router.post(
    "/supplier",
    status_code=201,
    dependencies=[require_roles("ADMIN", "INVENTORY_MANAGER")],
)
def create_supplier_return(
    body: SupplierReturnCreate,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    ret = service.create_supplier_return(db, body, current_user.id)
    return {"success": True, "data": _resp(ret), "message": "Supplier return created"}


@router.get("/{return_id}")
def get_return(return_id: int, db: Session = Depends(get_db)):
    ret = repository.get_return_by_id(db, return_id)
    if not ret:
        from app.common.exceptions import NotFoundError
        raise NotFoundError("Return", return_id)
    return {"success": True, "data": _resp(ret)}


def _resp(r) -> dict:
    items = []
    if hasattr(r, "items"):
        for i in r.items:
            med_name = i.medicine.name if hasattr(i, "medicine") and i.medicine else None
            items.append({
                "id": i.id,
                "medicine_id": i.medicine_id,
                "medicine_name": med_name,
                "batch_id": i.batch_id,
                "quantity": i.quantity,
                "unit_price": float(i.unit_price),
                "total_amount": float(i.total_amount),
                "condition_status": i.condition_status,
            })
    return {
        "id": r.id,
        "return_number": r.return_number,
        "return_type": r.return_type,
        "sale_id": r.sale_id,
        "purchase_id": r.purchase_id,
        "processed_by": r.processed_by,
        "return_date": r.return_date.isoformat() if r.return_date else None,
        "status": r.status,
        "reason": r.reason,
        "total_amount": float(r.total_amount),
        "notes": r.notes,
        "items": items,
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }
