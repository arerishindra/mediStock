"""
MediStock Backend — Sales Schemas
"""

from datetime import date, datetime

from pydantic import BaseModel, Field


class SaleItemCreate(BaseModel):
    medicine_id: int
    batch_id: int | None = None  # None = use FIFO
    quantity: int = Field(..., gt=0)


class SaleCreate(BaseModel):
    customer_name: str | None = None
    customer_phone: str | None = None
    sale_date: date
    items: list[SaleItemCreate] = Field(..., min_length=1)
    discount_amount: float = 0
    tax_amount: float = 0
    payment_method: str = "CASH"
    idempotency_key: str | None = None
    notes: str | None = None


class SaleResponse(BaseModel):
    id: int
    invoice_number: str
    sold_by: int
    customer_name: str | None
    customer_phone: str | None
    sale_date: date
    subtotal: float
    discount_amount: float
    tax_amount: float
    total_amount: float
    payment_method: str
    status: str
    items: list[dict] = []
    created_at: datetime

    model_config = {"from_attributes": True}
