"""
MediStock Backend — Inventory Schemas
"""

from datetime import date, datetime

from pydantic import BaseModel, Field


class BatchResponse(BaseModel):
    id: int
    medicine_id: int
    medicine_name: str | None = None
    supplier_id: int | None
    batch_number: str
    manufacturing_date: date | None
    expiry_date: date
    quantity_received: int
    current_quantity: int
    cost_price: float
    selling_price: float
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class StockMovementResponse(BaseModel):
    id: int
    batch_id: int
    batch_number: str | None = None
    movement_type: str
    quantity: int
    quantity_after: int
    reference_type: str
    reference_id: int
    performed_by: int
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class StockAdjustmentRequest(BaseModel):
    batch_id: int
    adjustment_type: str = Field(..., pattern="^(ADJUSTMENT_IN|ADJUSTMENT_OUT|WRITE_OFF)$")
    quantity: int = Field(..., gt=0)
    reason: str = Field(..., min_length=1, max_length=500)


class InventorySummaryItem(BaseModel):
    medicine_id: int
    medicine_name: str
    category_name: str | None
    total_quantity: int
    batch_count: int
    total_value: float
