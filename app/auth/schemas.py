import datetime
import uuid
from typing import Optional

from pydantic import BaseModel, HttpUrl

from app.utils import LikeStatus, UserSex, Zodiac


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
    sex: Optional[UserSex] = None
    bio: Optional[str] = None
    interests: Optional[list] = None
    city: Optional[str] = None
    zodiac: Optional[Zodiac] = None

    class Config:
        from_attributes = True


class UserUpdateSchema(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[UserSex] = None
    bio: Optional[str] = None
    interests: Optional[list] = None
    city: Optional[str] = None
    zodiac: Optional[Zodiac] = None


class AccessTokenOutSchema(BaseModel):
    access_token: str


class LikeCreateSchema(BaseModel):
    liked_user_id: uuid.UUID


class LikeSchema(BaseModel):
    user_id: uuid.UUID
    liked_user_id: uuid.UUID
    status: LikeStatus
    created_at: Optional[datetime.datetime]

    class Config:
        from_attributes = True


class MatchCreateSchema(BaseModel):
    user1_id: uuid.UUID
    user2_id: uuid.UUID


class MatchSchema(BaseModel):
    match_id: uuid.UUID
    user1_id: uuid.UUID
    user2_id: uuid.UUID
    created_at: Optional[datetime.datetime]

    class Config:
        from_attributes = True
