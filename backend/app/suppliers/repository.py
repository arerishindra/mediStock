"""
MediStock Backend — Supplier Repository
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.suppliers.models import Supplier


def get_supplier_by_id(db: Session, supplier_id: int) -> Supplier | None:
    return db.query(Supplier).filter(Supplier.id == supplier_id).first()


def get_supplier_by_name(db: Session, name: str) -> Supplier | None:
    return db.query(Supplier).filter(Supplier.name == name).first()


def list_suppliers_query(search: str | None = None, is_active: bool | None = None):
    query = select(Supplier).order_by(Supplier.name)
    if search:
        query = query.where(
            Supplier.name.ilike(f"%{search}%")
            | Supplier.contact_person.ilike(f"%{search}%")
        )
    if is_active is not None:
        query = query.where(Supplier.is_active == is_active)
    return query
