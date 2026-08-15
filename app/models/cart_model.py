from __future__ import annotations
from app.orm.postgres import AppBaseMixin, Base
from app.configs import config
import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from typing import TYPE_CHECKING
from uuid6 import uuid7

if TYPE_CHECKING:
    from app.models.user_model import User
    from app.models.cart_item_model import CartItem


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
    total_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_price: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Relationship
    user: Mapped["User"] = relationship()
    cart_items: Mapped[list["CartItem"]] = relationship(
        back_populates="cart",
        cascade="all, delete-orphan",
    )
