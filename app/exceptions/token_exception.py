from fastapi import status

from app.exceptions.base_exception import BaseAppException


class InvalidTokenError(BaseAppException):
    def __init__(self, detail: str = "Invalid or expired token"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="INVALID_TOKEN",
            headers={"WWW-Authenticate": "Bearer"},
        )


class ExpiredTokenError(InvalidTokenError):
    def __init__(self, detail: str = "Token has expired"):
        super().__init__(detail=detail)
        self.error_code = "EXPIRED_TOKEN"


class InvalidOTPError(BaseAppException):
    def __init__(self, detail: str = "Invalid or incorrect OTP"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="INVALID_OTP",
        )


class InvalidRefreshTokenError(BaseAppException):
    def __init__(self, detail: str = "Invalid or expired refresh token"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="INVALID_REFRESH_TOKEN",
        )


class RefreshTokenReusedError(InvalidRefreshTokenError):
    def __init__(self, detail: str = "Refresh token has already been used"):
        super().__init__(detail=detail)
        self.error_code = "REFRESH_TOKEN_REUSED"
