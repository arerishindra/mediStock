"""
MediStock Backend — Reports Service

Aggregation queries for dashboard and report endpoints.
"""

from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.alerts.models import Alert
from app.inventory.models import Batch, StockMovement
from app.medicines.models import Category, Medicine
from app.purchases.models import Purchase
from app.sales.models import Sale, SaleItem


def get_dashboard_summary(db: Session) -> dict:
    """Get dashboard summary cards."""
    today = date.today()

    total_medicines = db.query(func.count(Medicine.id)).filter(Medicine.is_active == True).scalar() or 0

    low_stock_count = (
        db.query(func.count(func.distinct(Medicine.id)))
        .outerjoin(Batch, (Batch.medicine_id == Medicine.id) & (Batch.is_active == True))
        .filter(Medicine.is_active == True)
        .group_by(Medicine.id)
        .having(func.coalesce(func.sum(Batch.current_quantity), 0) < Medicine.reorder_level)
        .count()
    ) or 0

    expiry_threshold = today + timedelta(days=90)
    expiring_count = (
        db.query(func.count(Batch.id))
        .filter(
            Batch.is_active == True,
            Batch.current_quantity > 0,
            Batch.expiry_date <= expiry_threshold,
        )
        .scalar()
    ) or 0

    today_sales = (
        db.query(func.coalesce(func.sum(Sale.total_amount), 0))
        .filter(Sale.sale_date == today)
        .scalar()
    ) or 0

    today_purchases = (
        db.query(func.coalesce(func.sum(Purchase.total_amount), 0))
        .filter(Purchase.purchase_date == today)
        .scalar()
    ) or 0

    active_alerts = (
        db.query(func.count(Alert.id))
        .filter(Alert.status == "ACTIVE")
        .scalar()
    ) or 0

    return {
        "total_medicines": total_medicines,
        "low_stock_count": low_stock_count,
        "expiring_soon_count": expiring_count,
        "today_sales_total": float(today_sales),
        "today_purchases_total": float(today_purchases),
        "active_alerts": active_alerts,
    }


def get_inventory_report(db: Session) -> list[dict]:
    """Current inventory valuation by medicine/batch."""
    results = (
        db.query(
            Medicine.id,
            Medicine.name,
            Category.name.label("category"),
            Batch.batch_number,
            Batch.current_quantity,
            Batch.cost_price,
            Batch.selling_price,
            Batch.expiry_date,
        )
        .join(Category, Medicine.category_id == Category.id)
        .join(Batch, Batch.medicine_id == Medicine.id)
        .filter(Batch.is_active == True, Batch.current_quantity > 0)
        .order_by(Medicine.name, Batch.expiry_date)
        .all()
    )

    return [
        {
            "medicine_id": r[0],
            "medicine_name": r[1],
            "category": r[2],
            "batch_number": r[3],
            "current_quantity": r[4],
            "cost_price": float(r[5]),
            "selling_price": float(r[6]),
            "stock_value": float(r[4] * r[6]),
            "expiry_date": r[7].isoformat() if r[7] else None,
        }
        for r in results
    ]


def get_sales_report(db: Session, start_date: date, end_date: date) -> dict:
    """Sales report for a date range."""
    sales = (
        db.query(
            func.count(Sale.id).label("total_sales"),
            func.coalesce(func.sum(Sale.total_amount), 0).label("total_revenue"),
            func.coalesce(func.sum(Sale.discount_amount), 0).label("total_discounts"),
        )
        .filter(Sale.sale_date.between(start_date, end_date))
        .first()
    )

    top_medicines = (
        db.query(
            Medicine.name,
            func.sum(SaleItem.quantity).label("qty_sold"),
            func.sum(SaleItem.total_price).label("revenue"),
        )
        .join(SaleItem, SaleItem.medicine_id == Medicine.id)
        .join(Sale, Sale.id == SaleItem.sale_id)
        .filter(Sale.sale_date.between(start_date, end_date))
        .group_by(Medicine.id, Medicine.name)
        .order_by(func.sum(SaleItem.quantity).desc())
        .limit(10)
        .all()
    )

    return {
        "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        "total_sales": sales[0] if sales else 0,
        "total_revenue": float(sales[1]) if sales else 0,
        "total_discounts": float(sales[2]) if sales else 0,
        "top_medicines": [
            {"name": m[0], "quantity_sold": int(m[1]), "revenue": float(m[2])}
            for m in top_medicines
        ],
    }


def get_purchases_report(db: Session, start_date: date, end_date: date) -> dict:
    """Purchase report for a date range."""
    result = (
        db.query(
            func.count(Purchase.id),
            func.coalesce(func.sum(Purchase.total_amount), 0),
        )
        .filter(Purchase.purchase_date.between(start_date, end_date))
        .first()
    )

    return {
        "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        "total_purchases": result[0] if result else 0,
        "total_amount": float(result[1]) if result else 0,
    }


def get_expiry_report(db: Session, days: int = 90) -> list[dict]:
    """Batches expiring within the given number of days."""
    threshold = date.today() + timedelta(days=days)
    results = (
        db.query(
            Medicine.name,
            Batch.batch_number,
            Batch.expiry_date,
            Batch.current_quantity,
            Batch.selling_price,
        )
        .join(Medicine, Batch.medicine_id == Medicine.id)
        .filter(
            Batch.is_active == True,
            Batch.current_quantity > 0,
            Batch.expiry_date <= threshold,
        )
        .order_by(Batch.expiry_date)
        .all()
    )

    return [
        {
            "medicine_name": r[0],
            "batch_number": r[1],
            "expiry_date": r[2].isoformat() if r[2] else None,
            "days_until_expiry": (r[2] - date.today()).days if r[2] else None,
            "current_quantity": r[3],
            "value_at_risk": float(r[3] * r[4]),
        }
        for r in results
    ]
