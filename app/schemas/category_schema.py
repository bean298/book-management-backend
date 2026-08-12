from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from app.models.category_model import Category
from datetime import datetime


class _CategoryBase(BaseModel):
    """Shared base fields for Category schemas."""

    name: str = Field(..., description="Name of category", max_length=255)
    description: Optional[str] = Field(
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

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1, max_length=500)


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
