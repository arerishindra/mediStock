"""
MediStock Backend — Medicine & Category Schemas
"""

from datetime import datetime

from pydantic import BaseModel, Field


# --- Category Schemas ---

class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None


class CategoryUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    is_active: bool | None = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Medicine Schemas ---

class MedicineCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    generic_name: str | None = None
    category_id: int
    manufacturer: str | None = None
    dosage_form: str = Field(..., min_length=1, max_length=50)
    strength: str = Field(..., min_length=1, max_length=50)
    unit: str = Field(..., min_length=1, max_length=50)
    reorder_level: int = 10
    description: str | None = None


class MedicineUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    generic_name: str | None = None
    category_id: int | None = None
    manufacturer: str | None = None
    dosage_form: str | None = None
    strength: str | None = None
    unit: str | None = None
    reorder_level: int | None = None
    description: str | None = None
    is_active: bool | None = None


class MedicineResponse(BaseModel):
    id: int
    name: str
    generic_name: str | None
    category_id: int
    category_name: str | None = None
    manufacturer: str | None
    dosage_form: str
    strength: str
    unit: str
    reorder_level: int
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
