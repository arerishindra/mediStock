"""
MediStock Backend — Medicine & Category Router
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import require_roles
from app.common.pagination import paginate
from app.db.session import get_db
from app.medicines import repository, service
from app.medicines.schemas import (
    CategoryCreate,
    CategoryUpdate,
    MedicineCreate,
    MedicineUpdate,
)

router = APIRouter(tags=["Medicines & Categories"])


# --- Category Endpoints ---

@router.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    """List all categories."""
    query = repository.list_categories_query()
    items, meta = paginate(db, query, page=1, page_size=100)
    return {
        "success": True,
        "data": {
            "items": [_cat_resp(c) for c in items],
            "pagination": meta.model_dump(),
        },
    }


@router.post(
    "/categories",
    status_code=201,
    dependencies=[require_roles("ADMIN", "INVENTORY_MANAGER")],
)
def create_category(body: CategoryCreate, db: Session = Depends(get_db)):
    cat = service.create_category(db, body)
    return {"success": True, "data": _cat_resp(cat), "message": "Category created"}


@router.get("/categories/{category_id}")
def get_category(category_id: int, db: Session = Depends(get_db)):
    cat = repository.get_category_by_id(db, category_id)
    if not cat:
        from app.common.exceptions import NotFoundError

        raise NotFoundError("Category", category_id)
    return {"success": True, "data": _cat_resp(cat)}


@router.put(
    "/categories/{category_id}",
    dependencies=[require_roles("ADMIN", "INVENTORY_MANAGER")],
)
def update_category(category_id: int, body: CategoryUpdate, db: Session = Depends(get_db)):
    cat = service.update_category(db, category_id, body)
    return {"success": True, "data": _cat_resp(cat), "message": "Category updated"}


@router.delete("/categories/{category_id}", dependencies=[require_roles("ADMIN")])
def deactivate_category(category_id: int, db: Session = Depends(get_db)):
    service.deactivate_category(db, category_id)
    return {"success": True, "message": "Category deactivated"}


# --- Medicine Endpoints ---

@router.get("/medicines")
def list_medicines(
    page: int = 1,
    page_size: int = 20,
    category_id: int | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
):
    """List medicines with filtering and pagination."""
    query = repository.list_medicines_query(category_id=category_id, search=search)
    items, meta = paginate(db, query, page, page_size)
    return {
        "success": True,
        "data": {
            "items": [_med_resp(m, db) for m in items],
            "pagination": meta.model_dump(),
        },
    }


@router.post(
    "/medicines",
    status_code=201,
    dependencies=[require_roles("ADMIN", "INVENTORY_MANAGER")],
)
def create_medicine(body: MedicineCreate, db: Session = Depends(get_db)):
    med = service.create_medicine(db, body)
    return {"success": True, "data": _med_resp(med, db), "message": "Medicine created"}


@router.get("/medicines/{medicine_id}")
def get_medicine(medicine_id: int, db: Session = Depends(get_db)):
    med = repository.get_medicine_by_id(db, medicine_id)
    if not med:
        from app.common.exceptions import NotFoundError

        raise NotFoundError("Medicine", medicine_id)
    return {"success": True, "data": _med_resp(med, db)}


@router.put(
    "/medicines/{medicine_id}",
    dependencies=[require_roles("ADMIN", "INVENTORY_MANAGER")],
)
def update_medicine(medicine_id: int, body: MedicineUpdate, db: Session = Depends(get_db)):
    med = service.update_medicine(db, medicine_id, body)
    return {"success": True, "data": _med_resp(med, db), "message": "Medicine updated"}


@router.delete("/medicines/{medicine_id}", dependencies=[require_roles("ADMIN")])
def deactivate_medicine(medicine_id: int, db: Session = Depends(get_db)):
    service.deactivate_medicine(db, medicine_id)
    return {"success": True, "message": "Medicine deactivated"}


def _cat_resp(cat) -> dict:
    return {
        "id": cat.id,
        "name": cat.name,
        "description": cat.description,
        "is_active": cat.is_active,
        "created_at": cat.created_at.isoformat() if cat.created_at else None,
    }


def _med_resp(med, db=None) -> dict:
    cat_name = None
    if hasattr(med, "category") and med.category:
        cat_name = med.category.name
    return {
        "id": med.id,
        "name": med.name,
        "generic_name": med.generic_name,
        "category_id": med.category_id,
        "category_name": cat_name,
        "manufacturer": med.manufacturer,
        "dosage_form": med.dosage_form,
        "strength": med.strength,
        "unit": med.unit,
        "reorder_level": med.reorder_level,
        "description": med.description,
        "is_active": med.is_active,
        "created_at": med.created_at.isoformat() if med.created_at else None,
        "updated_at": med.updated_at.isoformat() if med.updated_at else None,
    }
