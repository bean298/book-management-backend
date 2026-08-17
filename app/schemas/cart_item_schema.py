from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from app.models.cart_item_model import CartItem


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


class CartItemRes(_CartItemBase):
    """Schema for cart response."""

    id: str = Field(..., description="Cart ID")
    book_title: str = Field(..., description="Book title")
    book_description: str = Field(..., description="Book description")
    created_at: datetime
