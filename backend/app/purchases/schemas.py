"""
MediStock Backend — Purchase Schemas
"""

from datetime import date, datetime

from pydantic import BaseModel, Field


class PurchaseItemCreate(BaseModel):
    medicine_id: int
    quantity: int = Field(..., gt=0)
    unit_cost: float = Field(..., gt=0)


class PurchaseCreate(BaseModel):
    supplier_id: int
    purchase_date: date
    items: list[PurchaseItemCreate] = Field(..., min_length=1)
    notes: str | None = None


class PurchaseReceiveItem(BaseModel):
    purchase_item_id: int
    quantity_received: int = Field(..., gt=0)
    batch_number: str = Field(..., min_length=1)
    manufacturing_date: date | None = None
    expiry_date: date
    selling_price: float = Field(..., gt=0)


class PurchaseReceiveRequest(BaseModel):
    items: list[PurchaseReceiveItem] = Field(..., min_length=1)


class PurchaseResponse(BaseModel):
    id: int
    purchase_number: str
    supplier_id: int
    supplier_name: str | None = None
    created_by: int
    purchase_date: date
    status: str
    total_amount: float
    notes: str | None
    items: list[dict] = []
    created_at: datetime

    model_config = {"from_attributes": True}
