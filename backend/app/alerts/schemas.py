"""
MediStock Backend — Alerts Schemas
"""

from datetime import datetime

from pydantic import BaseModel


class AlertResponse(BaseModel):
    id: int
    alert_type: str
    medicine_id: int
    medicine_name: str | None = None
    batch_id: int | None
    message: str
    status: str
    acknowledged_by: int | None
    acknowledged_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
