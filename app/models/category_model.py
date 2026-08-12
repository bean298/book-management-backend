from __future__ import annotations
from app.orm.postgres import AppBaseMixin, Base
from app.configs import config
import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import UUID
from uuid6 import uuid7

if TYPE_CHECKING:
    from app.models.book_model import Book


class Category(AppBaseMixin, Base):
    __tablename__ = config.CATEGORY_TABLE
    __table_args__ = {"schema": config.BOOK_SCHEMA}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid7, unique=True
    )
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationship with Book model
    books: Mapped[list[Book]] = relationship(back_populates="category")
