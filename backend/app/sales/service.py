"""
MediStock Backend — Sales Service

Handles atomic sale creation with FIFO batch deduction and stock movement recording.
"""

from datetime import date, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from app.common.exceptions import (
    BusinessRuleError,
    DuplicateError,
    ExpiredBatchError,
    InsufficientStockError,
)
from app.inventory.models import Batch
from app.inventory.service import record_stock_movement
from app.sales.models import Sale, SaleItem
from app.sales.repository import (
    get_next_invoice_number,
    get_sale_by_id,
    get_sale_by_idempotency_key,
)
from app.sales.schemas import SaleCreate


def create_sale(db: Session, data: SaleCreate, user_id: int) -> Sale:
    """
    Create a sale with atomic stock deduction.
    Supports explicit batch selection or FIFO (earliest expiry first).
    """
    # Idempotency check
    if data.idempotency_key:
        existing = get_sale_by_idempotency_key(db, data.idempotency_key)
        if existing:
            return get_sale_by_id(db, existing.id)

    invoice_number = get_next_invoice_number(db)
    today = date.today()

    sale = Sale(
        invoice_number=invoice_number,
        sold_by=user_id,
        customer_name=data.customer_name,
        customer_phone=data.customer_phone,
        sale_date=data.sale_date,
        discount_amount=data.discount_amount,
        tax_amount=data.tax_amount,
        payment_method=data.payment_method,
        idempotency_key=data.idempotency_key,
        notes=data.notes,
    )
    db.add(sale)
    db.flush()

    subtotal = Decimal("0")

    for item_data in data.items:
        if item_data.batch_id:
            # Explicit batch selection
            batch = db.query(Batch).filter(Batch.id == item_data.batch_id).first()
            if not batch:
                raise BusinessRuleError(f"Batch {item_data.batch_id} not found")
            if batch.expiry_date < today:
                raise ExpiredBatchError(batch.batch_number, str(batch.expiry_date))
            if batch.current_quantity < item_data.quantity:
                raise InsufficientStockError(
                    batch.batch_number, batch.current_quantity, item_data.quantity
                )

            item_price = Decimal(str(batch.selling_price)) * Decimal(str(item_data.quantity))
            sale_item = SaleItem(
                sale_id=sale.id,
                medicine_id=item_data.medicine_id,
                batch_id=batch.id,
                quantity=item_data.quantity,
                unit_price=float(batch.selling_price),
                total_price=float(item_price),
            )
            db.add(sale_item)
            subtotal += item_price

            # Deduct stock
            record_stock_movement(
                db=db,
                batch_id=batch.id,
                movement_type="SALE",
                quantity=-item_data.quantity,
                reference_type="SALE",
                reference_id=sale.id,
                performed_by=user_id,
            )
        else:
            # FIFO: deduct from earliest-expiring batches
            remaining = item_data.quantity
            batches = (
                db.query(Batch)
                .filter(
                    Batch.medicine_id == item_data.medicine_id,
                    Batch.current_quantity > 0,
                    Batch.is_active == True,
                    Batch.expiry_date >= today,
                )
                .order_by(Batch.expiry_date)
                .all()
            )

            if sum(b.current_quantity for b in batches) < remaining:
                raise InsufficientStockError(
                    f"Medicine {item_data.medicine_id}",
                    sum(b.current_quantity for b in batches),
                    remaining,
                )

            for batch in batches:
                if remaining <= 0:
                    break

                deduct = min(remaining, batch.current_quantity)
                item_price = Decimal(str(batch.selling_price)) * Decimal(str(deduct))

                sale_item = SaleItem(
                    sale_id=sale.id,
                    medicine_id=item_data.medicine_id,
                    batch_id=batch.id,
                    quantity=deduct,
                    unit_price=float(batch.selling_price),
                    total_price=float(item_price),
                )
                db.add(sale_item)
                subtotal += item_price

                record_stock_movement(
                    db=db,
                    batch_id=batch.id,
                    movement_type="SALE",
                    quantity=-deduct,
                    reference_type="SALE",
                    reference_id=sale.id,
                    performed_by=user_id,
                )

                remaining -= deduct

    sale.subtotal = float(subtotal)
    sale.total_amount = float(
        subtotal - Decimal(str(data.discount_amount)) + Decimal(str(data.tax_amount))
    )

    db.commit()
    return get_sale_by_id(db, sale.id)
