import uuid
from typing import Optional

from pydantic import BaseModel, HttpUrl

from app.utils import UserSex


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
    age: Optional[int]
    sex: Optional[UserSex]

    class Config:
        from_attributes = True


class AccessTokenOutSchema(BaseModel):
    access_token: str
