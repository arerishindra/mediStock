"""
MediStock Backend — Pagination Utilities

Shared pagination logic for list endpoints.
"""

import math

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.common.responses import PaginatedData, PaginationMeta


def paginate(
    db: Session,
    query: Select,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list, PaginationMeta]:
    """
    Apply pagination to a SQLAlchemy select query.

    Returns (items, pagination_meta).
    """
    page = max(1, page)
    page_size = max(1, min(100, page_size))

    # Count total rows
    count_query = select(func.count()).select_from(query.subquery())
    total = db.execute(count_query).scalar() or 0

    total_pages = math.ceil(total / page_size) if total > 0 else 0

    # Fetch page
    offset = (page - 1) * page_size
    items = db.execute(query.offset(offset).limit(page_size)).scalars().all()

    meta = PaginationMeta(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )

    return list(items), meta
