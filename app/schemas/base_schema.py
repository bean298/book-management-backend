from datetime import datetime
from http import HTTPStatus
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class AppBasePagingRes(BaseModel, Generic[T]):
    items: list[T] = []
    total: int = Field(None, description="Total number of items")
    is_full: bool = Field(None, description="Whether the current page is full")
    page: int | None = Field(None, description="Current page number")
    page_size: int | None = Field(None, description="Number of items per page")


class AppBaseResponse(BaseModel, Generic[T]):
    data: T | None = None
    success: bool = True
    message: str | None = ""
    status_code: int = HTTPStatus.OK
    error_code: int | None = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    total: int | None = None
