from __future__ import annotations
from app.orm.postgres import AppBaseMixin, Base
from app.configs import config
import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Text

if TYPE_CHECKING:
    from app.models.book_model import Book


class Category(AppBaseMixin, Base):
    __tablename__ = config.CATEGORY_TABLE
    __table_args__ = {"schema": config.BOOK_SCHEMA}

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid7())
    )
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationship with Book model
    books: Mapped[list[Book]] = relationship(back_populates="category")
