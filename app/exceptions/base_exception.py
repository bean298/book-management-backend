from fastapi import HTTPException


class BaseAppException(HTTPException):
    """Base custom exception for the application"""

    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str | None = None,
        headers: dict[str, str] | None = None,
    ):
        super().__init__(
            status_code=status_code,
            detail=detail,
            headers=headers,
        )
        self.error_code = error_code
