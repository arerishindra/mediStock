"""
MediStock Backend — Returns Repository
"""

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.returns.models import Return, ReturnItem


def get_return_by_id(db: Session, return_id: int) -> Return | None:
    return (
        db.query(Return)
        .options(
            joinedload(Return.items).joinedload(ReturnItem.medicine),
            joinedload(Return.items).joinedload(ReturnItem.batch),
        )
        .filter(Return.id == return_id)
        .first()
    )


def list_returns_query(return_type: str | None = None, status: str | None = None):
    query = select(Return).order_by(Return.created_at.desc())
    if return_type:
        query = query.where(Return.return_type == return_type)
    if status:
        query = query.where(Return.status == status)
    return query


def get_next_return_number(db: Session) -> str:
    last = db.query(Return).order_by(Return.id.desc()).first()
    next_num = (last.id + 1) if last else 1
    return f"RET-{next_num:06d}"
