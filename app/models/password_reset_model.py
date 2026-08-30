import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from uuid6 import uuid7

from app.configs import config
from app.enum.common import ResetMethod
from app.orm.postgres import AppBaseMixin, Base


class PasswordResetToken(AppBaseMixin, Base):
    __tablename__ = config.PASSWORD_RESET_TABLE
    __table_args__ = {"schema": config.AUTH_SCHEMA}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid7, unique=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{config.AUTH_SCHEMA}.users.id", ondelete="CASCADE"),
    )
    method: Mapped[ResetMethod] = mapped_column(
        Enum(ResetMethod), nullable=False
    )
    otp_code: Mapped[str | None] = mapped_column(String(6), nullable=True)
    token: Mapped[str | None] = mapped_column(String(512), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
