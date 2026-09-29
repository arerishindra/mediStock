"""
MediStock Backend — Reports Schemas
"""

from datetime import date

from pydantic import BaseModel


class DateRangeQuery(BaseModel):
    start_date: date
    end_date: date
