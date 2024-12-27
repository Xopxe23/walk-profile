import uuid
from typing import Optional

from pydantic import BaseModel, HttpUrl

from app.models.users import UserSexEnum, ZodiacEnum


class AccessTokenOutSchema(BaseModel):
    access_token: str


class TelegramUserInSchema(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    photo_url: Optional[HttpUrl] = None
    auth_date: int
    hash: str


class UserSchema(BaseModel):
    user_id: uuid.UUID
    telegram_id: int
    name: str
    age: Optional[int] = None
    sex: Optional[UserSexEnum] = None
    bio: Optional[str] = None
    interests: Optional[list] = None
    city: Optional[str] = None
    zodiac: Optional[ZodiacEnum] = None

    class Config:
        from_attributes = True


class UserUpdateSchema(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[UserSexEnum] = None
    bio: Optional[str] = None
    interests: Optional[list] = None
    city: Optional[str] = None
    zodiac: Optional[ZodiacEnum] = None
