from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid6 import uuid7

from app.configs import config
from app.orm.postgres import AppBaseMixin, Base

if TYPE_CHECKING:
    from app.models.cart_item_model import CartItem
    from app.models.user_model import User


class Cart(AppBaseMixin, Base):
    __tablename__ = config.CART_TABLE
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
        unique=True,
    )
    total_quantity: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    total_price: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False
    )

    # Relationship
    user: Mapped[User] = relationship()
    cart_items: Mapped[list[CartItem]] = relationship(
        back_populates="cart",
        cascade="all, delete-orphan",
    )
