from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid6 import uuid7

from app.configs import config
from app.orm.postgres import AppBaseMixin, Base

if TYPE_CHECKING:
    from app.models.author_model import Author
    from app.models.category_model import Category


class Book(AppBaseMixin, Base):
    __tablename__ = config.BOOK_TABLE
    __table_args__ = {"schema": config.BOOK_SCHEMA}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid7, unique=True
    )
    title: Mapped[str] = mapped_column(String(255))
    published_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey(f"{config.BOOK_SCHEMA}.authors.id")
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey(f"{config.BOOK_SCHEMA}.categories.id")
    )
    cover_image: Mapped[str | None] = mapped_column(String(255), nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    # Relationships to take author, category when query book
    author: Mapped[Author] = relationship(back_populates="books")
    category: Mapped[Category] = relationship(back_populates="books")
