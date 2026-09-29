"""
MediStock Backend — Medicine Repository
"""

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.medicines.models import Category, Medicine


# --- Category ---

def get_category_by_id(db: Session, category_id: int) -> Category | None:
    return db.query(Category).filter(Category.id == category_id).first()


def get_category_by_name(db: Session, name: str) -> Category | None:
    return db.query(Category).filter(Category.name == name).first()


def list_categories_query():
    return select(Category).order_by(Category.name)


# --- Medicine ---

def get_medicine_by_id(db: Session, medicine_id: int) -> Medicine | None:
    return (
        db.query(Medicine)
        .options(joinedload(Medicine.category))
        .filter(Medicine.id == medicine_id)
        .first()
    )


def list_medicines_query(
    category_id: int | None = None,
    search: str | None = None,
    is_active: bool | None = None,
):
    query = select(Medicine).order_by(Medicine.name)
    if category_id:
        query = query.where(Medicine.category_id == category_id)
    if search:
        query = query.where(
            Medicine.name.ilike(f"%{search}%")
            | Medicine.generic_name.ilike(f"%{search}%")
        )
    if is_active is not None:
        query = query.where(Medicine.is_active == is_active)
    return query
