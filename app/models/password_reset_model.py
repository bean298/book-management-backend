from app.orm.postgres import AppBaseMixin, Base
from app.configs import config
import uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.enum.common import ResetMethod


class PasswordResetToken(AppBaseMixin, Base):
    __tablename__ = config.PASSWORD_RESET_TABLE
    __table_args__ = {"schema": config.AUTH_SCHEMA}

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid7())
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{config.AUTH_SCHEMA}.users.id", ondelete="CASCADE"),
    )
    method: Mapped[ResetMethod] = mapped_column(Enum(ResetMethod), nullable=False)
    otp_code: Mapped[str | None] = mapped_column(String(6), nullable=True)
    token: Mapped[str | None] = mapped_column(String(512), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
