from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.book_model import Book
from app.utils.build_slug import build_slug
from app.utils.image import resolve_images


class _BookBase(BaseModel):
    """Shared base fields for Book schemas."""

    title: str = Field(..., description="Book title", max_length=255)
    author_id: UUID = Field(..., description="Author ID")
    category_id: UUID = Field(..., description="Category ID")
    published_year: int | None = Field(default=None, description="Published year")
    cover_image: str | None = Field(
        default=None, max_length=500, description="Cover image URL"
    )
    price: float = Field(..., description="Book price")
    quantity: int = Field(default=0, description="Quantity in stock")
    description: str | None = Field(
        default=None, max_length=2000, description="Book description"
    )


class CreateBookReq(_BookBase):
    """Schema for creating a new book."""

    pass


class UpdateBookReq(BaseModel):
    """Schema for updating book."""

    title: str | None = Field(..., description="Book title", max_length=255)
    published_year: int | None = Field(default=None, description="Published year")
    cover_image: str | None = Field(
        default=None, max_length=500, description="Cover image URL"
    )
    price: float | None = Field(..., description="Book price")
    quantity: int | None = Field(default=0, description="Quantity in stock")
    description: str | None = Field(
        default=None, max_length=2000, description="Book description"
    )


class BookRes(_BookBase):
    """Schema for book response."""

    id: str = Field(..., description="Book ID")
    slug: str = Field(..., description="URL slug")
    created_at: datetime


def req_to_book(data: CreateBookReq) -> Book:
    return Book(
        title=data.title,
        author_id=data.author_id,
        category_id=data.category_id,
        published_year=data.published_year,
        cover_image=data.cover_image,
        price=data.price,
        quantity=data.quantity,
        description=data.description,
        slug=build_slug(data.title),
    )


# Convert ORM model → Pydantic schema for JSON response
def book_to_res(book: Book) -> BookRes:
    return BookRes(
        id=str(book.id),
        title=book.title,
        author_id=book.author_id,
        category_id=book.category_id,
        published_year=book.published_year,
        cover_image=resolve_images(book.cover_image),
        price=book.price,
        quantity=book.quantity,
        description=book.description,
        slug=book.slug,
        created_at=book.created_at.isoformat() if book.created_at else None,
    )
