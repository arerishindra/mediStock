"""
MediStock Backend — Supplier Schemas
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class SupplierCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    contact_person: str | None = None
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=50)
    address: str | None = None
    tax_id: str | None = Field(None, max_length=100)
    payment_terms: str | None = Field(None, max_length=100)


class SupplierUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    contact_person: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    address: str | None = None
    tax_id: str | None = None
    payment_terms: str | None = None
    is_active: bool | None = None


class SupplierResponse(BaseModel):
    id: int
    name: str
    contact_person: str | None
    email: str | None
    phone: str | None
    address: str | None
    tax_id: str | None
    payment_terms: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
