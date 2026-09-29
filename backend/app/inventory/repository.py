"""
MediStock Backend — Inventory Repository
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.inventory.models import Batch, StockMovement
from app.medicines.models import Medicine


def get_batch_by_id(db: Session, batch_id: int) -> Batch | None:
    return (
        db.query(Batch)
        .options(joinedload(Batch.medicine))
        .filter(Batch.id == batch_id)
        .first()
    )


def list_batches_for_medicine(db: Session, medicine_id: int):
    return (
        select(Batch)
        .where(Batch.medicine_id == medicine_id)
        .order_by(Batch.expiry_date)
    )


def list_stock_movements_query(
    batch_id: int | None = None,
    movement_type: str | None = None,
    medicine_id: int | None = None,
):
    query = select(StockMovement).order_by(StockMovement.created_at.desc())
    if batch_id:
        query = query.where(StockMovement.batch_id == batch_id)
    if movement_type:
        query = query.where(StockMovement.movement_type == movement_type)
    if medicine_id:
        query = query.join(Batch).where(Batch.medicine_id == medicine_id)
    return query


def get_inventory_summary(db: Session):
    """Get stock summary grouped by medicine."""
    results = (
        db.query(
            Medicine.id,
            Medicine.name,
            func.sum(Batch.current_quantity).label("total_qty"),
            func.count(Batch.id).label("batch_count"),
            func.sum(Batch.current_quantity * Batch.selling_price).label("total_value"),
        )
        .join(Batch, Batch.medicine_id == Medicine.id)
        .filter(Batch.is_active == True, Medicine.is_active == True)
        .group_by(Medicine.id, Medicine.name)
        .order_by(Medicine.name)
        .all()
    )
    return results
