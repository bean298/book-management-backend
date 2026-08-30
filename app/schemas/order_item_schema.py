from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class _OrderItemBase(BaseModel):
    """Shared base fields for Order item schemas."""

    order_id: UUID = Field(..., description="Order ID")
    book_id: UUID = Field(..., description="Book ID")
    book_name: str = Field(..., min_length=1, description="Book name")
    quantity: int = Field(default=0, description="Quantity")
    unit_price: float = Field(..., description="Price")


class OrderItemRes(_OrderItemBase):
    """Schema for Order response."""

    id: str = Field(..., description="Order item ID")
    book_description: str = Field(..., description="Book description")
    cover_image: str | None = Field(
        default=None, max_length=500, description="Cover image URL"
    )
    created_at: datetime
