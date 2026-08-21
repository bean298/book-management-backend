from __future__ import annotations
from app.orm.postgres import AppBaseMixin, Base
from app.configs import config
import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from typing import TYPE_CHECKING
from uuid6 import uuid7

if TYPE_CHECKING:
    from app.models.order_model import Order
    from app.models.book_model import Book


class OrderItem(AppBaseMixin, Base):
    __tablename__ = config.ORDER_ITEMS_TABLE
    __table_args__ = (
        UniqueConstraint("order_id", "book_id", name="uq_order_item_order_book"),
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
    order: Mapped["Order"] = relationship(back_populates="order_items")
    book: Mapped["Book"] = relationship()
