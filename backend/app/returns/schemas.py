"""
MediStock Backend — Returns Schemas
"""

from datetime import date

from pydantic import BaseModel, Field


class ReturnItemCreate(BaseModel):
    medicine_id: int
    batch_id: int
    quantity: int = Field(..., gt=0)
    condition_status: str = "RESTOCKED"  # RESTOCKED, QUARANTINED, WRITTEN_OFF


class CustomerReturnCreate(BaseModel):
    sale_id: int
    return_date: date
    reason: str = Field(..., min_length=1, max_length=500)
    items: list[ReturnItemCreate] = Field(..., min_length=1)
    notes: str | None = None


class SupplierReturnCreate(BaseModel):
    purchase_id: int
    return_date: date
    reason: str = Field(..., min_length=1, max_length=500)
    items: list[ReturnItemCreate] = Field(..., min_length=1)
    notes: str | None = None


class ProcessReturnRequest(BaseModel):
    """Process a pending return — set condition for each item."""

    items: list[dict] = Field(
        ...,
        min_length=1,
        description="List of {return_item_id, condition_status} dicts",
    )
