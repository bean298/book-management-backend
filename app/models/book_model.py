from __future__ import annotations
from app.orm.postgres import AppBaseMixin, Base
from app.configs import config
import uuid
from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy import String
from sqlalchemy import String, Integer, ForeignKey
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.author_model import Author
    from app.models.category_model import Category


class Book(AppBaseMixin, Base):
    __tablename__ = config.BOOK_TABLE
    __table_args__ = {"schema": config.BOOK_SCHEMA}

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid7())
    )
    title: Mapped[str] = mapped_column(String(255))
    published_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    author_id: Mapped[str] = mapped_column(
        String(36), ForeignKey(f"{config.BOOK_SCHEMA}.authors.id")
    )
    category_id: Mapped[str] = mapped_column(
        String(36), ForeignKey(f"{config.BOOK_SCHEMA}.categories.id")
    )
    cover_image: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships to take author, category when query book
    author: Mapped["Author"] = relationship(back_populates="books")
    category: Mapped["Category"] = relationship(back_populates="books")
