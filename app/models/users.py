import datetime
import enum
import uuid

from sqlalchemy import JSON, TIMESTAMP, Enum, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class UserSexEnum(enum.Enum):
    male = "M"
    female = "F"


class ZodiacEnum(enum.Enum):
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


class Users(Base):
    __tablename__ = "users"

    user_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    telegram_id: Mapped[int]
    name: Mapped[str]
    age: Mapped[int] = mapped_column(nullable=True)
    sex: Mapped[UserSexEnum] = mapped_column(Enum(UserSexEnum), nullable=True)
    bio: Mapped[str] = mapped_column(nullable=True)
    photo_url: Mapped[str] = mapped_column(nullable=True)
    interests: Mapped[list] = mapped_column(JSON, nullable=True)
    city: Mapped[str] = mapped_column(nullable=True)
    zodiac: Mapped[ZodiacEnum] = mapped_column(Enum(ZodiacEnum), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, server_default=text("NOW()"))
