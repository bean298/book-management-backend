from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid6 import uuid7

from app.configs import config
from app.enum.common import PaymentMethod, PaymentStatus
from app.orm.postgres import AppBaseMixin, Base

if TYPE_CHECKING:
    from app.models.order_model import Order
    from app.models.user_model import User


class Payment(AppBaseMixin, Base):
    __tablename__ = config.PAYMENT_TABLE
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
    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            f"{config.COMMERCE_SCHEMA}.{config.ORDER_TABLE}.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    payment_method: Mapped[PaymentMethod] = mapped_column(
        Enum(PaymentMethod), default=PaymentMethod.CASH, nullable=False
    )
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False
    )

    transaction_ref: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    # Data return from VNPay
    gateway_txn_no: Mapped[str | None] = mapped_column(String(100), nullable=True)
    bank_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    pay_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Raw data return from VNPay
    raw_callback: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    order: Mapped[Order] = relationship()
    user: Mapped[User] = relationship()
