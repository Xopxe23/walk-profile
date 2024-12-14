from fastapi import status

from app.utils import CustomHTTPException


class InvalidTelegramDataException(CustomHTTPException):
    STATUS_CODE = status.HTTP_400_BAD_REQUEST
    DETAIL = "Invalid telegram auth data"
