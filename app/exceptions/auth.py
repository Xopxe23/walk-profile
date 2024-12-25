from fastapi import status

from app.exceptions.common import NotFoundException
from app.utils import CustomHTTPException


class InvalidTelegramDataException(CustomHTTPException):
    STATUS_CODE = status.HTTP_400_BAD_REQUEST
    DETAIL = "Invalid telegram auth data"


class UserNotFoundException(NotFoundException):
    DETAIL = "User not found"


class LikeExistsException(CustomHTTPException):
    STATUS_CODE = status.HTTP_409_CONFLICT
    DETAIL = "Like already exists"


class MatchExistsException(CustomHTTPException):
    STATUS_CODE = status.HTTP_409_CONFLICT
    DETAIL = "Match already exists"


class InvalidTokenException(CustomHTTPException):
    STATUS_CODE = status.HTTP_401_UNAUTHORIZED
    DETAIL = "Token is not valid"

    def __init__(self) -> None:
        super().__init__(headers={"WWW-Authenticate": "Bearer"})
