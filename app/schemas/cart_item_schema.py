from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


class _CartItemBase(BaseModel):
    """Shared base fields for Cart item schemas."""

    cart_id: UUID = Field(..., description="Cart ID")
    book_id: UUID = Field(..., description="Book ID")
    quantity: int = Field(default=0, description="Quantity")
    unit_price: float = Field(..., description="Price")


class AddToCartReq(BaseModel):
    """Schema for creating a new cart item."""

    book_id: UUID = Field(..., description="Book ID")
    quantity: int = Field(default=0, description="Quantity")


class UpdateCartItemReq(BaseModel):
    quantity: int = Field(gt=0)


class CartItemRes(_CartItemBase):
    """Schema for cart response."""

    id: str = Field(..., description="Cart ID")
    book_title: str = Field(..., description="Book title")
    book_description: str = Field(..., description="Book description")
    cover_image: Optional[str] = Field(
        default=None, max_length=500, description="Cover image URL"
    )
    created_at: datetime
