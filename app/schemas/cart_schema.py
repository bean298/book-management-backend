from pydantic import BaseModel, Field
from app.models.cart_model import Cart
from app.models.cart_item_model import CartItem
from uuid import UUID
from datetime import datetime
from app.schemas.cart_item_schema import CartItemRes
from app.utils.image import resolve_images


class _CartBase(BaseModel):
    """Shared base fields for Cart schemas."""

    user_id: UUID = Field(..., description="User ID")
    total_quantity: int = Field(default=0, description="Total quantity")
    total_price: float = Field(..., description="Total price")


class CartRes(_CartBase):
    """Schema for cart response."""

    id: str = Field(..., description="Cart ID")
    cart_items: list[CartItemRes]
    created_at: datetime


def cart_to_res(cart: Cart, cart_items: list[CartItem], user_id: str) -> CartRes:
    return CartRes(
        id=str(cart.id),
        user_id=user_id,
        total_quantity=cart.total_quantity,
        total_price=cart.total_price,
        created_at=cart.created_at,
        cart_items=[
            CartItemRes(
                id=str(item.id),
                cart_id=str(item.cart_id),
                book_id=str(item.book_id),
                book_title=item.book.title,
                book_description=item.book.description,
                cover_image=resolve_images(item.book.cover_image),
                quantity=item.quantity,
                unit_price=item.unit_price,
                created_at=item.created_at,
            )
            for item in cart_items
        ],
    )
