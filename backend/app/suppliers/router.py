"""
MediStock Backend — Supplier Router
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import require_roles
from app.common.pagination import paginate
from app.db.session import get_db
from app.suppliers import repository, service
from app.suppliers.schemas import SupplierCreate, SupplierUpdate

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


@router.get("")
def list_suppliers(
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    db: Session = Depends(get_db),
):
    query = repository.list_suppliers_query(search=search)
    items, meta = paginate(db, query, page, page_size)
    return {
        "success": True,
        "data": {
            "items": [_resp(s) for s in items],
            "pagination": meta.model_dump(),
        },
    }


@router.post(
    "",
    status_code=201,
    dependencies=[require_roles("ADMIN", "INVENTORY_MANAGER")],
)
def create_supplier(body: SupplierCreate, db: Session = Depends(get_db)):
    sup = service.create_supplier(db, body)
    return {"success": True, "data": _resp(sup), "message": "Supplier created"}


@router.get("/{supplier_id}")
def get_supplier(supplier_id: int, db: Session = Depends(get_db)):
    sup = repository.get_supplier_by_id(db, supplier_id)
    if not sup:
        from app.common.exceptions import NotFoundError
        raise NotFoundError("Supplier", supplier_id)
    return {"success": True, "data": _resp(sup)}


@router.put(
    "/{supplier_id}",
    dependencies=[require_roles("ADMIN", "INVENTORY_MANAGER")],
)
def update_supplier(supplier_id: int, body: SupplierUpdate, db: Session = Depends(get_db)):
    sup = service.update_supplier(db, supplier_id, body)
    return {"success": True, "data": _resp(sup), "message": "Supplier updated"}


@router.delete("/{supplier_id}", dependencies=[require_roles("ADMIN")])
def deactivate_supplier(supplier_id: int, db: Session = Depends(get_db)):
    service.deactivate_supplier(db, supplier_id)
    return {"success": True, "message": "Supplier deactivated"}


def _resp(s) -> dict:
    return {
        "id": s.id,
        "name": s.name,
        "contact_person": s.contact_person,
        "email": s.email,
        "phone": s.phone,
        "address": s.address,
        "tax_id": s.tax_id,
        "payment_terms": s.payment_terms,
        "is_active": s.is_active,
        "created_at": s.created_at.isoformat() if s.created_at else None,
        "updated_at": s.updated_at.isoformat() if s.updated_at else None,
    }
