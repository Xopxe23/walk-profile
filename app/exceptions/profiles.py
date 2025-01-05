from fastapi import status

from app.exceptions.common import CustomHTTPException, NotFoundException


class UserNotFoundException(NotFoundException):
    DETAIL = "User not found"


class ProfileNotCompletedException(CustomHTTPException):
    STATUS_CODE = status.HTTP_400_BAD_REQUEST
    DETAIL = "Profile is not completed"


class LikeExistsException(CustomHTTPException):
    STATUS_CODE = status.HTTP_409_CONFLICT
    DETAIL = "Like already exists"


class MatchExistsException(CustomHTTPException):
    STATUS_CODE = status.HTTP_409_CONFLICT
    DETAIL = "Match already exists"
