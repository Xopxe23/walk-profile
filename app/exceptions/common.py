from typing import Any

from fastapi import HTTPException, status


class CustomHTTPException(HTTPException):
    """Кастомный exception для наследования"""

    STATUS_CODE = status.HTTP_500_INTERNAL_SERVER_ERROR
    DETAIL = "Server error"

    def __init__(self, **kwargs: dict[str, Any]) -> None:
        super().__init__(status_code=self.STATUS_CODE, detail=self.DETAIL, **kwargs)


class NotFoundException(CustomHTTPException):
    DETAIL = "Not found"
    STATUS_CODE = status.HTTP_404_NOT_FOUND
