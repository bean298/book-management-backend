from fastapi import status
from app.exceptions.base_exception import BaseAppException


class BadRequestError(BaseAppException):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="BAD_REQUEST",
        )


class ConflictError(BaseAppException):
    def __init__(self, detail: str = "Conflict", error_code: str = "CONFLICT"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code=error_code,
        )


class NotFoundError(BaseAppException):
    def __init__(self, resource: str = "Resource", resource_id: str = None):
        detail = f"{resource} not found"
        if resource_id:
            detail = f"{resource} with id '{resource_id}' not found"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code=f"{resource.upper()}_NOT_FOUND",
        )


class DuplicateError(BaseAppException):
    def __init__(
        self, resource: str = "Resource", field: str = None, value: str = None
    ):
        detail = f"{resource} already exists"
        if field and value:
            detail = f"{resource} with {field} '{value}' already exists"
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code=f"{resource.upper()}_DUPLICATE",
        )
