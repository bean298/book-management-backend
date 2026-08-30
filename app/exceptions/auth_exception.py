from fastapi import status

from app.exceptions.base_exception import BaseAppException


class InvalidCredentialsError(BaseAppException):
    def __init__(self, detail: str = "Invalid email or password"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="INVALID_CREDENTIALS",
        )


class EmailAlreadyRegisteredError(BaseAppException):
    def __init__(self, detail: str = "Email already registered"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="EMAIL_ALREADY_REGISTERED",
        )


class UserNotFoundError(BaseAppException):
    def __init__(self, detail: str = "User not found"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="USER_NOT_FOUND",
        )


class AdminAccessRequiredError(BaseAppException):
    def __init__(self, detail: str = "Admin access required"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="ADMIN_ACCESS_REQUIRED",
        )
