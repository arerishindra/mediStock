"""
MediStock Backend — Supplier Service
"""

from sqlalchemy.orm import Session

from app.common.exceptions import DuplicateError, NotFoundError
from app.suppliers.models import Supplier
from app.suppliers.repository import get_supplier_by_id, get_supplier_by_name
from app.suppliers.schemas import SupplierCreate, SupplierUpdate


def create_supplier(db: Session, data: SupplierCreate) -> Supplier:
    if get_supplier_by_name(db, data.name):
        raise DuplicateError("Supplier", "name", data.name)

    supplier = Supplier(**data.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


def update_supplier(db: Session, supplier_id: int, data: SupplierUpdate) -> Supplier:
    supplier = get_supplier_by_id(db, supplier_id)
    if not supplier:
        raise NotFoundError("Supplier", supplier_id)

    if data.name and data.name != supplier.name:
        if get_supplier_by_name(db, data.name):
            raise DuplicateError("Supplier", "name", data.name)

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(supplier, key, value)

    db.commit()
    db.refresh(supplier)
    return supplier


def deactivate_supplier(db: Session, supplier_id: int) -> Supplier:
    supplier = get_supplier_by_id(db, supplier_id)
    if not supplier:
        raise NotFoundError("Supplier", supplier_id)
    supplier.is_active = False
    db.commit()
    return supplier
