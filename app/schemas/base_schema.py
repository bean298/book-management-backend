from app.enum.common import OBJECT_STATUS
from pydantic import BaseModel, Field
from typing import Generic, Optional, TypeVar

T = TypeVar("T")


class AppBasePagingRes(BaseModel, Generic[T]):
    items: list[T] = []
    total: int = Field(None, description="Total number of items")
    is_full: bool = Field(None, description="Whether the current page is full")
    page: Optional[int] = Field(None, description="Current page number")
    page_size: Optional[int] = Field(None, description="Number of items per page")
