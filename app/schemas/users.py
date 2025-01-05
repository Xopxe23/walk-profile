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
    photo_url: Optional[HttpUrl] = None
    interests: Optional[list[str]] = None
    city: Optional[str] = None
    zodiac: Optional[ZodiacEnum] = None

    def dict(self, **kwargs):
        data = super().dict(**kwargs)
        if 'user_id' in data:
            data['user_id'] = str(data['user_id'])
        if 'sex' in data and data['sex']:
            data['sex'] = data['sex'].value
        if 'zodiac' in data and data['zodiac']:
            data['zodiac'] = data['zodiac'].value
        return data

    class Config:
        from_attributes = True


class UserUpdateSchema(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[UserSexEnum] = None
    bio: Optional[str] = None
    interests: Optional[list[str]] = None
    city: Optional[str] = None
    zodiac: Optional[ZodiacEnum] = None


class UserUpdatePhotoSchema(BaseModel):
    photo_url: str


class UserDocumentSchema(BaseModel):
    user_id: str
    sex: Optional[str] = None
    interests: Optional[list[str]] = None
    city: Optional[str] = None
