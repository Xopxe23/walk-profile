from fastapi import status

from app.exceptions.common import CustomHTTPException


class InvalidTelegramDataException(CustomHTTPException):
    STATUS_CODE = status.HTTP_400_BAD_REQUEST
    DETAIL = "Invalid telegram auth data"


class InvalidTokenException(CustomHTTPException):
    STATUS_CODE = status.HTTP_401_UNAUTHORIZED
    DETAIL = "Token is not valid"

    def __init__(self) -> None:
        super().__init__(headers={"WWW-Authenticate": "Bearer"})
