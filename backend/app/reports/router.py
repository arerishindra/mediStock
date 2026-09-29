"""
MediStock Backend — Reports & Dashboard Router
"""

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.reports import service

router = APIRouter(tags=["Reports & Dashboard"])


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    """Dashboard summary cards."""
    data = service.get_dashboard_summary(db)
    return {"success": True, "data": data}


@router.get("/reports/inventory")
def inventory_report(db: Session = Depends(get_db)):
    """Current inventory valuation."""
    data = service.get_inventory_report(db)
    return {"success": True, "data": {"items": data}}


@router.get("/reports/sales")
def sales_report(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
):
    """Sales report for a date range."""
    data = service.get_sales_report(db, start_date, end_date)
    return {"success": True, "data": data}


@router.get("/reports/purchases")
def purchases_report(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
):
    """Purchase report for a date range."""
    data = service.get_purchases_report(db, start_date, end_date)
    return {"success": True, "data": data}


@router.get("/reports/expiry")
def expiry_report(
    days: int = Query(90, ge=1, le=365),
    db: Session = Depends(get_db),
):
    """Expiry report — batches expiring within N days."""
    data = service.get_expiry_report(db, days)
    return {"success": True, "data": {"items": data}}
