import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from uuid6 import uuid7

from app.configs import config
from app.orm.postgres import AppBaseMixin, Base


class RefreshToken(AppBaseMixin, Base):
    __tablename__ = config.REFRESH_TOKEN_TABLE
    __table_args__ = {"schema": config.AUTH_SCHEMA}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid7
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            f"{config.AUTH_SCHEMA}.{config.USER_TABLE}.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    revoked: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    replaced_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
