"""
MediStock Backend — Returns Service

Handles customer and supplier returns with stock movement recording.
"""

from decimal import Decimal

from sqlalchemy.orm import Session

from app.common.exceptions import BusinessRuleError, NotFoundError
from app.inventory.models import Batch
from app.inventory.service import record_stock_movement
from app.returns.models import Return, ReturnItem
from app.returns.repository import get_next_return_number, get_return_by_id
from app.returns.schemas import CustomerReturnCreate, SupplierReturnCreate


def create_customer_return(
    db: Session, data: CustomerReturnCreate, user_id: int
) -> Return:
    """Create a customer return linked to an original sale."""
    return_number = get_next_return_number(db)

    ret = Return(
        return_number=return_number,
        return_type="CUSTOMER",
        sale_id=data.sale_id,
        processed_by=user_id,
        return_date=data.return_date,
        reason=data.reason,
        notes=data.notes,
    )
    db.add(ret)
    db.flush()

    total = Decimal("0")
    for item_data in data.items:
        batch = db.query(Batch).filter(Batch.id == item_data.batch_id).first()
        if not batch:
            raise NotFoundError("Batch", item_data.batch_id)

        unit_price = batch.selling_price
        item_total = Decimal(str(unit_price)) * Decimal(str(item_data.quantity))

        ret_item = ReturnItem(
            return_id=ret.id,
            medicine_id=item_data.medicine_id,
            batch_id=item_data.batch_id,
            quantity=item_data.quantity,
            unit_price=float(unit_price),
            total_amount=float(item_total),
            condition_status=item_data.condition_status,
        )
        db.add(ret_item)
        total += item_total

        # Restock if condition is RESTOCKED
        if item_data.condition_status == "RESTOCKED":
            record_stock_movement(
                db=db,
                batch_id=batch.id,
                movement_type="CUSTOMER_RETURN",
                quantity=item_data.quantity,
                reference_type="RETURN",
                reference_id=ret.id,
                performed_by=user_id,
                notes=f"Customer return: {data.reason}",
            )
        elif item_data.condition_status == "WRITTEN_OFF":
            # Record as write-off (no quantity change — it was already deducted)
            record_stock_movement(
                db=db,
                batch_id=batch.id,
                movement_type="WRITE_OFF",
                quantity=0,
                reference_type="RETURN",
                reference_id=ret.id,
                performed_by=user_id,
                notes=f"Written off from customer return: {data.reason}",
            )

    ret.total_amount = float(total)
    ret.status = "PROCESSED"
    db.commit()
    return get_return_by_id(db, ret.id)


def create_supplier_return(
    db: Session, data: SupplierReturnCreate, user_id: int
) -> Return:
    """Create a supplier return — deducts stock."""
    return_number = get_next_return_number(db)

    ret = Return(
        return_number=return_number,
        return_type="SUPPLIER",
        purchase_id=data.purchase_id,
        processed_by=user_id,
        return_date=data.return_date,
        reason=data.reason,
        notes=data.notes,
    )
    db.add(ret)
    db.flush()

    total = Decimal("0")
    for item_data in data.items:
        batch = db.query(Batch).filter(Batch.id == item_data.batch_id).first()
        if not batch:
            raise NotFoundError("Batch", item_data.batch_id)

        unit_price = batch.cost_price
        item_total = Decimal(str(unit_price)) * Decimal(str(item_data.quantity))

        ret_item = ReturnItem(
            return_id=ret.id,
            medicine_id=item_data.medicine_id,
            batch_id=item_data.batch_id,
            quantity=item_data.quantity,
            unit_price=float(unit_price),
            total_amount=float(item_total),
            condition_status=item_data.condition_status,
        )
        db.add(ret_item)
        total += item_total

        # Deduct stock for supplier return
        record_stock_movement(
            db=db,
            batch_id=batch.id,
            movement_type="SUPPLIER_RETURN",
            quantity=-item_data.quantity,
            reference_type="RETURN",
            reference_id=ret.id,
            performed_by=user_id,
            notes=f"Supplier return: {data.reason}",
        )

    ret.total_amount = float(total)
    ret.status = "PROCESSED"
    db.commit()
    return get_return_by_id(db, ret.id)
