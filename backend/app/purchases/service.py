"""
MediStock Backend — Purchase Service

Handles purchase creation and atomic receiving (creates batches + stock movements).
"""

from decimal import Decimal

from sqlalchemy.orm import Session

from app.common.exceptions import BusinessRuleError, NotFoundError
from app.inventory.models import Batch
from app.inventory.service import record_stock_movement
from app.purchases.models import Purchase, PurchaseItem
from app.purchases.repository import get_next_purchase_number, get_purchase_by_id
from app.purchases.schemas import PurchaseCreate, PurchaseReceiveRequest
from app.suppliers.repository import get_supplier_by_id


def create_purchase(db: Session, data: PurchaseCreate, user_id: int) -> Purchase:
    """Create a new purchase order."""
    if not get_supplier_by_id(db, data.supplier_id):
        raise NotFoundError("Supplier", data.supplier_id)

    purchase_number = get_next_purchase_number(db)

    purchase = Purchase(
        purchase_number=purchase_number,
        supplier_id=data.supplier_id,
        created_by=user_id,
        purchase_date=data.purchase_date,
        status="ORDERED",
        notes=data.notes,
    )
    db.add(purchase)
    db.flush()

    total = Decimal("0")
    for item_data in data.items:
        item_total = Decimal(str(item_data.quantity)) * Decimal(str(item_data.unit_cost))
        item = PurchaseItem(
            purchase_id=purchase.id,
            medicine_id=item_data.medicine_id,
            quantity=item_data.quantity,
            unit_cost=item_data.unit_cost,
            total_cost=float(item_total),
        )
        db.add(item)
        total += item_total

    purchase.total_amount = float(total)
    db.commit()
    return get_purchase_by_id(db, purchase.id)


def receive_purchase(
    db: Session, purchase_id: int, data: PurchaseReceiveRequest, user_id: int
) -> Purchase:
    """
    Atomically receive a purchase: create batches, record stock movements,
    update purchase item received quantities, and update purchase status.
    """
    purchase = get_purchase_by_id(db, purchase_id)
    if not purchase:
        raise NotFoundError("Purchase", purchase_id)

    if purchase.status in ("RECEIVED", "CANCELLED"):
        raise BusinessRuleError(f"Purchase {purchase.purchase_number} is already {purchase.status}")

    # Map purchase items by ID for lookup
    pi_map = {pi.id: pi for pi in purchase.items}

    for recv in data.items:
        pi = pi_map.get(recv.purchase_item_id)
        if not pi:
            raise NotFoundError("PurchaseItem", recv.purchase_item_id)

        remaining = pi.quantity - pi.quantity_received
        if recv.quantity_received > remaining:
            raise BusinessRuleError(
                f"Cannot receive {recv.quantity_received} units for item {pi.id}; "
                f"only {remaining} remaining"
            )

        # Create batch
        batch = Batch(
            medicine_id=pi.medicine_id,
            supplier_id=purchase.supplier_id,
            batch_number=recv.batch_number,
            manufacturing_date=recv.manufacturing_date,
            expiry_date=recv.expiry_date,
            quantity_received=recv.quantity_received,
            current_quantity=0,
            cost_price=float(pi.unit_cost),
            selling_price=recv.selling_price,
        )
        db.add(batch)
        db.flush()

        # Record stock movement
        record_stock_movement(
            db=db,
            batch_id=batch.id,
            movement_type="PURCHASE_RECEIPT",
            quantity=recv.quantity_received,
            reference_type="PURCHASE",
            reference_id=purchase.id,
            performed_by=user_id,
            notes=f"Received via {purchase.purchase_number}",
        )

        # Update purchase item
        pi.quantity_received += recv.quantity_received
        pi.batch_id = batch.id

    # Update purchase status
    all_received = all(pi.quantity_received >= pi.quantity for pi in purchase.items)
    any_received = any(pi.quantity_received > 0 for pi in purchase.items)

    if all_received:
        purchase.status = "RECEIVED"
    elif any_received:
        purchase.status = "PARTIALLY_RECEIVED"

    db.commit()
    return get_purchase_by_id(db, purchase.id)


def cancel_purchase(db: Session, purchase_id: int) -> Purchase:
    """Cancel a purchase order."""
    purchase = get_purchase_by_id(db, purchase_id)
    if not purchase:
        raise NotFoundError("Purchase", purchase_id)

    if purchase.status == "RECEIVED":
        raise BusinessRuleError("Cannot cancel a fully received purchase")

    purchase.status = "CANCELLED"
    db.commit()
    return purchase
