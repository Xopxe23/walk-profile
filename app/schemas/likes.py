import datetime
import uuid
from typing import Optional

from pydantic import BaseModel

from app.models.likes import LikeStatusEnum


class LikeCreateSchema(BaseModel):
    liked_user_id: uuid.UUID


class LikeSchema(BaseModel):
    like_id: uuid.UUID
    user_id: uuid.UUID
    liked_user_id: uuid.UUID
    status: LikeStatusEnum
    created_at: Optional[datetime.datetime]

    class Config:
        from_attributes = True
