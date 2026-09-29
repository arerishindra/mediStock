"""
MediStock Backend — Standard Response Schemas

Pydantic schemas for consistent API responses.
"""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ErrorDetail(BaseModel):
    """Error detail in API responses."""

    code: str
    message: str
    details: dict[str, Any] | None = None


class ApiResponse(BaseModel, Generic[T]):
    """Standard API response envelope."""

    success: bool
    data: T | None = None
    message: str | None = None
    error: ErrorDetail | None = None


class PaginationMeta(BaseModel):
    """Pagination metadata."""

    total: int
    page: int
    page_size: int
    total_pages: int


class PaginatedData(BaseModel, Generic[T]):
    """Paginated data with metadata."""

    items: list[T]
    pagination: PaginationMeta
