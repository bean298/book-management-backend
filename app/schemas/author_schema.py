from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from uuid import UUID
from app.models.author_model import Author
from datetime import datetime


class _AuthorBase(BaseModel):
    """Shared base fields for Author schemas."""

    name: str = Field(..., description="Name of author", max_length=255)
    bio: Optional[str] = Field(
        default=None, description="Biography of author", max_length=500
    )


class AuthorCreateReq(_AuthorBase):
    """Schema for registering a new author."""

    pass


class AuthorRes(_AuthorBase):
    """Schema for author response."""

    id: UUID
    name: str
    created_at: datetime


class UpdateAuthorReq(BaseModel):
    """Schema for updating author."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    bio: Optional[str] = Field(None, min_length=1, max_length=255)


def req_to_author(data: AuthorCreateReq) -> Author:
    return Author(
        name=data.name,
        bio=data.bio,
    )


# Convert ORM model → Pydantic schema for JSON response
def author_to_res(author: Author) -> AuthorRes:
    return AuthorRes(
        id=author.id,
        bio=author.bio,
        name=author.name,
        created_at=author.created_at,
    )
