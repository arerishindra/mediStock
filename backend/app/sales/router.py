"""
MediStock Backend — Sales Router
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import CurrentUser, require_roles
from app.common.pagination import paginate
from app.db.session import get_db
from app.sales import repository, service
from app.sales.schemas import SaleCreate

router = APIRouter(prefix="/sales", tags=["Sales"])


@router.get("")
def list_sales(
    page: int = 1,
    page_size: int = 20,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    query = repository.list_sales_query(status=status)
    items, meta = paginate(db, query, page, page_size)
    return {
        "success": True,
        "data": {
            "items": [_resp(s, db) for s in items],
            "pagination": meta.model_dump(),
        },
    }


@router.post(
    "",
    status_code=201,
    dependencies=[require_roles("ADMIN", "PHARMACIST")],
)
def create_sale(
    body: SaleCreate,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    sale = service.create_sale(db, body, current_user.id)
    return {"success": True, "data": _resp(sale, db), "message": "Sale created"}


@router.get("/{sale_id}")
def get_sale(sale_id: int, db: Session = Depends(get_db)):
    sale = repository.get_sale_by_id(db, sale_id)
    if not sale:
        from app.common.exceptions import NotFoundError
        raise NotFoundError("Sale", sale_id)
    return {"success": True, "data": _resp(sale, db)}


@router.get("/{sale_id}/invoice")
def get_invoice(sale_id: int, db: Session = Depends(get_db)):
    """Get printable invoice data."""
    sale = repository.get_sale_by_id(db, sale_id)
    if not sale:
        from app.common.exceptions import NotFoundError
        raise NotFoundError("Sale", sale_id)
    return {"success": True, "data": _resp(sale, db)}


def _resp(s, db) -> dict:
    items = []
    if hasattr(s, "items"):
        for i in s.items:
            med_name = i.medicine.name if hasattr(i, "medicine") and i.medicine else None
            batch_num = i.batch.batch_number if hasattr(i, "batch") and i.batch else None
            items.append({
                "id": i.id,
                "medicine_id": i.medicine_id,
                "medicine_name": med_name,
                "batch_id": i.batch_id,
                "batch_number": batch_num,
                "quantity": i.quantity,
                "unit_price": float(i.unit_price),
                "total_price": float(i.total_price),
            })
    return {
        "id": s.id,
        "invoice_number": s.invoice_number,
        "sold_by": s.sold_by,
        "customer_name": s.customer_name,
        "customer_phone": s.customer_phone,
        "sale_date": s.sale_date.isoformat() if s.sale_date else None,
        "subtotal": float(s.subtotal),
        "discount_amount": float(s.discount_amount),
        "tax_amount": float(s.tax_amount),
        "total_amount": float(s.total_amount),
        "payment_method": s.payment_method,
        "status": s.status,
        "items": items,
        "created_at": s.created_at.isoformat() if s.created_at else None,
    }
