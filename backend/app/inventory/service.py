"""
MediStock Backend — Inventory Service

Stock adjustment operations with atomic transactions and ledger recording.
"""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.common.exceptions import BusinessRuleError, InsufficientStockError, NotFoundError
from app.inventory.models import Batch, StockMovement
from app.inventory.repository import get_batch_by_id
from app.inventory.schemas import StockAdjustmentRequest


def create_stock_adjustment(
    db: Session,
    data: StockAdjustmentRequest,
    user_id: int,
) -> StockMovement:
    """
    Create a stock adjustment (IN, OUT, or WRITE_OFF).
    Updates batch quantity and creates a ledger entry atomically.
    """
    batch = get_batch_by_id(db, data.batch_id)
    if not batch:
        raise NotFoundError("Batch", data.batch_id)

    if data.adjustment_type in ("ADJUSTMENT_OUT", "WRITE_OFF"):
        if batch.current_quantity < data.quantity:
            raise InsufficientStockError(
                batch.batch_number, batch.current_quantity, data.quantity
            )
        signed_qty = -data.quantity
    else:  # ADJUSTMENT_IN
        signed_qty = data.quantity

    # Update batch quantity
    batch.current_quantity += signed_qty
    new_qty = batch.current_quantity

    # Create stock movement ledger entry
    movement = StockMovement(
        batch_id=batch.id,
        movement_type=data.adjustment_type,
        quantity=signed_qty,
        quantity_after=new_qty,
        reference_type="ADJUSTMENT",
        reference_id=0,  # No linked entity for manual adjustments
        performed_by=user_id,
        notes=data.reason,
    )
    db.add(movement)
    db.commit()
    db.refresh(movement)
    return movement


def record_stock_movement(
    db: Session,
    batch_id: int,
    movement_type: str,
    quantity: int,
    reference_type: str,
    reference_id: int,
    performed_by: int,
    notes: str | None = None,
) -> StockMovement:
    """
    Low-level helper to record a stock movement and update batch quantity.
    Called by purchase, sale, and return services.
    """
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise NotFoundError("Batch", batch_id)

    batch.current_quantity += quantity
    if batch.current_quantity < 0:
        raise BusinessRuleError(
            f"Stock for batch {batch.batch_number} would go negative"
        )

    movement = StockMovement(
        batch_id=batch_id,
        movement_type=movement_type,
        quantity=quantity,
        quantity_after=batch.current_quantity,
        reference_type=reference_type,
        reference_id=reference_id,
        performed_by=performed_by,
        notes=notes,
    )
    db.add(movement)
    return movement
