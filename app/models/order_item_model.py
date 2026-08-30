from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid6 import uuid7

from app.configs import config
from app.orm.postgres import AppBaseMixin, Base

if TYPE_CHECKING:
    from app.models.book_model import Book
    from app.models.order_model import Order


class OrderItem(AppBaseMixin, Base):
    __tablename__ = config.ORDER_ITEMS_TABLE
    __table_args__ = (
        UniqueConstraint(
            "order_id", "book_id", name="uq_order_item_order_book"
        ),
        {"schema": config.COMMERCE_SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid7, unique=True
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            f"{config.COMMERCE_SCHEMA}.{config.ORDER_TABLE}.id",
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
    book_name: Mapped[str] = mapped_column(String(255), nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Relationships
    order: Mapped[Order] = relationship(back_populates="order_items")
    book: Mapped[Book] = relationship()
