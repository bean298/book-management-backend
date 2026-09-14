from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.enum.common import OrderStatus
from app.models.order_item_model import OrderItem
from app.models.order_model import Order
from app.models.user_model import User
from app.schemas.order_item_schema import OrderItemRes
from app.utils.image import resolve_images


class _OrderBase(BaseModel):
    """Shared base fields for Order schemas."""

    shipping_address: str = Field(..., min_length=1, description="Shipping address")


class CreateOrderReq(_OrderBase):
    """Schema for creating a new order."""

    pass


class UpdateOrderReq(BaseModel):
    """Schema for updating order status."""

    status: OrderStatus


class OrderUserRes(BaseModel):
    """Information of user in order."""

    id: UUID = Field(..., description="User ID")
    name: str = Field(..., description="User name")
    email: str = Field(..., description="User email")
    phone: int = Field(..., description="User phone")


class OrderRes(_OrderBase):
    """Schema for order response."""

    id: str = Field(..., description="Order ID")
    user: OrderUserRes = Field(..., description="User info")
    total_quantity: int
    total_price: float
    status: OrderStatus
    expires_at: datetime | None = Field(..., description="Payment deadline")
    order_items: list[OrderItemRes]
    created_at: datetime


def order_to_res(order: Order, order_items: list[OrderItem], user: User) -> OrderRes:
    return OrderRes(
        id=str(order.id),
        user=OrderUserRes(id=user.id, name=user.name, email=user.email, phone=user.phone),
        total_quantity=order.total_quantity,
        total_price=order.total_price,
        created_at=order.created_at,
        shipping_address=order.shipping_address,
        status=order.status,
        expires_at=order.expires_at,
        order_items=[
            OrderItemRes(
                id=str(item.id),
                order_id=str(item.order_id),
                book_id=str(item.book_id),
                book_name=item.book.title,
                book_description=item.book.description,
                cover_image=resolve_images(item.book.cover_image),
                quantity=item.quantity,
                unit_price=item.unit_price,
                created_at=item.created_at,
            )
            for item in order_items
        ],
    )
