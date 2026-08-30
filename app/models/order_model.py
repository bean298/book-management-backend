from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, Float, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid6 import uuid7

from app.configs import config
from app.enum.common import OrderStatus, PaymentMethod
from app.orm.postgres import AppBaseMixin, Base

if TYPE_CHECKING:
    from app.models.order_item_model import OrderItem
    from app.models.user_model import User


class Order(AppBaseMixin, Base):
    __tablename__ = config.ORDER_TABLE
    __table_args__ = {"schema": config.COMMERCE_SCHEMA}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid7, unique=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            f"{config.AUTH_SCHEMA}.{config.USER_TABLE}.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    total_quantity: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    total_price: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False
    )
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False
    )
    payment_method: Mapped[PaymentMethod] = mapped_column(
        Enum(PaymentMethod), default=PaymentMethod.CASH, nullable=False
    )
    shipping_address: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationship
    user: Mapped[User] = relationship()
    order_items: Mapped[list[OrderItem]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )
