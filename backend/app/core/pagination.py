from collections.abc import Sequence
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Generic pagination parameters validated from query strings."""
    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page (max 100)")
    sort_by: str | None = Field(default=None, description="Field name to sort by")
    sort_order: str = Field(default="asc", pattern="^(asc|desc)$", description="Sort direction (asc or desc)")

    @property
    def offset(self) -> int:
        """Calculate SQL offset based on page and page_size."""
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""
    items: Sequence[T]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool

    @classmethod
    def create(cls, items: Sequence[T], total_count: int, params: PaginationParams) -> "PaginatedResponse[T]":
        """Factory method computing page metadata."""
        total_pages = (total_count + params.page_size - 1) // params.page_size if params.page_size > 0 else 1
        return cls(
            items=items,
            total_count=total_count,
            page=params.page,
            page_size=params.page_size,
            total_pages=total_pages,
            has_next=params.page < total_pages,
            has_prev=params.page > 1,
        )
