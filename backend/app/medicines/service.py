"""
MediStock Backend — Medicine Service
"""

from sqlalchemy.orm import Session

from app.common.exceptions import DuplicateError, NotFoundError
from app.medicines.models import Category, Medicine
from app.medicines.repository import (
    get_category_by_id,
    get_category_by_name,
    get_medicine_by_id,
)
from app.medicines.schemas import CategoryCreate, CategoryUpdate, MedicineCreate, MedicineUpdate


# --- Category Service ---

def create_category(db: Session, data: CategoryCreate) -> Category:
    if get_category_by_name(db, data.name):
        raise DuplicateError("Category", "name", data.name)
    cat = Category(name=data.name, description=data.description)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


def update_category(db: Session, category_id: int, data: CategoryUpdate) -> Category:
    cat = get_category_by_id(db, category_id)
    if not cat:
        raise NotFoundError("Category", category_id)
    if data.name and data.name != cat.name:
        if get_category_by_name(db, data.name):
            raise DuplicateError("Category", "name", data.name)
        cat.name = data.name
    if data.description is not None:
        cat.description = data.description
    if data.is_active is not None:
        cat.is_active = data.is_active
    db.commit()
    db.refresh(cat)
    return cat


def deactivate_category(db: Session, category_id: int) -> Category:
    cat = get_category_by_id(db, category_id)
    if not cat:
        raise NotFoundError("Category", category_id)
    cat.is_active = False
    db.commit()
    return cat


# --- Medicine Service ---

def create_medicine(db: Session, data: MedicineCreate) -> Medicine:
    # Validate category exists
    if not get_category_by_id(db, data.category_id):
        raise NotFoundError("Category", data.category_id)

    # Check unique constraint
    existing = (
        db.query(Medicine)
        .filter(
            Medicine.name == data.name,
            Medicine.strength == data.strength,
            Medicine.dosage_form == data.dosage_form,
        )
        .first()
    )
    if existing:
        raise DuplicateError(
            "Medicine", "name+strength+dosage_form", f"{data.name}/{data.strength}/{data.dosage_form}"
        )

    med = Medicine(**data.model_dump())
    db.add(med)
    db.commit()
    db.refresh(med)
    return get_medicine_by_id(db, med.id)


def update_medicine(db: Session, medicine_id: int, data: MedicineUpdate) -> Medicine:
    med = get_medicine_by_id(db, medicine_id)
    if not med:
        raise NotFoundError("Medicine", medicine_id)

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(med, key, value)

    db.commit()
    db.refresh(med)
    return med


def deactivate_medicine(db: Session, medicine_id: int) -> Medicine:
    med = get_medicine_by_id(db, medicine_id)
    if not med:
        raise NotFoundError("Medicine", medicine_id)
    med.is_active = False
    db.commit()
    return med
