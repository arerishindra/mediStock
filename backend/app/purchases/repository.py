"""
MediStock Backend — Purchase Repository
"""

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.purchases.models import Purchase, PurchaseItem


def get_purchase_by_id(db: Session, purchase_id: int) -> Purchase | None:
    return (
        db.query(Purchase)
        .options(
            joinedload(Purchase.items).joinedload(PurchaseItem.medicine),
            joinedload(Purchase.supplier),
        )
        .filter(Purchase.id == purchase_id)
        .first()
    )


def list_purchases_query(supplier_id: int | None = None, status: str | None = None):
    query = select(Purchase).order_by(Purchase.created_at.desc())
    if supplier_id:
        query = query.where(Purchase.supplier_id == supplier_id)
    if status:
        query = query.where(Purchase.status == status)
    return query


def get_next_purchase_number(db: Session) -> str:
    """Generate the next sequential purchase number."""
    last = (
        db.query(Purchase)
        .order_by(Purchase.id.desc())
        .first()
    )
    next_num = (last.id + 1) if last else 1
    return f"PO-{next_num:06d}"
