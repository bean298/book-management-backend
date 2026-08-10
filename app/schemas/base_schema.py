from app.enum.common import OBJECT_STATUS
from pydantic import BaseModel, Field
from typing import Generic, Optional, TypeVar
from http import HTTPStatus
from datetime import datetime

T = TypeVar("T")


class AppBasePagingRes(BaseModel, Generic[T]):
    items: list[T] = []
    total: int = Field(None, description="Total number of items")
    is_full: bool = Field(None, description="Whether the current page is full")
    page: Optional[int] = Field(None, description="Current page number")
    page_size: Optional[int] = Field(None, description="Number of items per page")


class AppBaseResponse(BaseModel, Generic[T]):
    data: Optional[T] = None
    success: bool = True
    message: Optional[str] = ""
    status_code: int = HTTPStatus.OK
    error_code: Optional[int] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    total: Optional[int] = None
