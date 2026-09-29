"""
MediStock Backend — Sales Repository
"""

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.sales.models import Sale, SaleItem


def get_sale_by_id(db: Session, sale_id: int) -> Sale | None:
    return (
        db.query(Sale)
        .options(
            joinedload(Sale.items).joinedload(SaleItem.medicine),
            joinedload(Sale.items).joinedload(SaleItem.batch),
        )
        .filter(Sale.id == sale_id)
        .first()
    )


def get_sale_by_idempotency_key(db: Session, key: str) -> Sale | None:
    return db.query(Sale).filter(Sale.idempotency_key == key).first()


def list_sales_query(status: str | None = None):
    query = select(Sale).order_by(Sale.created_at.desc())
    if status:
        query = query.where(Sale.status == status)
    return query


def get_next_invoice_number(db: Session) -> str:
    last = db.query(Sale).order_by(Sale.id.desc()).first()
    next_num = (last.id + 1) if last else 1
    return f"INV-{next_num:06d}"
