import enum
import uuid
from typing import Annotated, Any

from fastapi import HTTPException, status
from sqlalchemy.orm import mapped_column

uuid_pk = Annotated[uuid.UUID, mapped_column(primary_key=True, default=uuid.uuid4)]  # UUID для Base models


class UserSex(enum.Enum):
    male = "M"
    female = "F"


class LikeStatus(enum.Enum):
    new = "new"
    seen = "seen"
    match = "match"


class MatchStatusEnum(enum.Enum):
    new = "new"
    seen = "seen"
    deleted = "deleted"


class Zodiac(enum.Enum):
    aries = "aries"
    taurus = "taurus"
    gemini = "gemini"
    cancer = "cancer"
    leo = "leo"
    virgo = "virgo"
    libra = "libra"
    scorpio = "scorpio"
    sagittarius = "sagittarius"
    capricorn = "capricorn"
    aquarius = "aquarius"
    pisces = "pisces"


class CustomHTTPException(HTTPException):
    """Кастомный exception для наследования"""

    STATUS_CODE = status.HTTP_500_INTERNAL_SERVER_ERROR
    DETAIL = "Server error"

    def __init__(self, **kwargs: dict[str, Any]) -> None:
        super().__init__(status_code=self.STATUS_CODE, detail=self.DETAIL, **kwargs)
