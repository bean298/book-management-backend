from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid6 import uuid7

from app.configs import config
from app.orm.postgres import AppBaseMixin, Base

if TYPE_CHECKING:
    from app.models.book_model import Book
    from app.models.cart_model import Cart


class CartItem(AppBaseMixin, Base):
    __tablename__ = config.CART_ITEMS_TABLE
    __table_args__ = (
        # One product only show 1 times, need time add will increase quantity
        UniqueConstraint("cart_id", "book_id", name="uq_cart_item_cart_book"),
        {"schema": config.COMMERCE_SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid7, unique=True
    )
    cart_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            f"{config.COMMERCE_SCHEMA}.{config.CART_TABLE}.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    book_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            f"{config.BOOK_SCHEMA}.{config.BOOK_TABLE}.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)

    # Relationships
    cart: Mapped[Cart] = relationship(back_populates="cart_items")
    book: Mapped[Book] = relationship()
