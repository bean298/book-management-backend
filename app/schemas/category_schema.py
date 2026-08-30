from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.category_model import Category


class _CategoryBase(BaseModel):
    """Shared base fields for Category schemas."""

    name: str = Field(..., description="Name of category", max_length=255)
    description: str | None = Field(
        default=None, description="Description of category", max_length=500
    )


class CategoryCreateReq(_CategoryBase):
    """Schema for creating a new category."""

    pass


class CategoryRes(_CategoryBase):
    """Schema for category response."""

    id: UUID
    created_at: datetime


class UpdateCategoryReq(BaseModel):
    """Schema for updating category."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, min_length=1, max_length=500)


def req_to_category(data: CategoryCreateReq) -> Category:
    return Category(
        name=data.name,
        description=data.description,
    )


# Convert ORM model → Pydantic schema for JSON response
def category_to_res(category: Category) -> CategoryRes:
    return CategoryRes(
        id=category.id,
        name=category.name,
        description=category.description,
        created_at=category.created_at,
    )
