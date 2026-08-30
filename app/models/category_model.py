from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid6 import uuid7

from app.configs import config
from app.orm.postgres import AppBaseMixin, Base

if TYPE_CHECKING:
    from app.models.book_model import Book


class Category(AppBaseMixin, Base):
    __tablename__ = config.CATEGORY_TABLE
    __table_args__ = {"schema": config.BOOK_SCHEMA}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid7, unique=True
    )
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationship with Book model
    books: Mapped[list[Book]] = relationship(back_populates="category")
