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

    def dict(self, **kwargs):
        data = super().dict(**kwargs)
        if 'like_id' in data:
            data['like_id'] = str(data['like_id'])
        if 'user_id' in data:
            data['user_id'] = str(data['user_id'])
        if 'liked_user_id' in data:
            data['liked_user_id'] = str(data['liked_user_id'])
        if 'status' in data:
            data['status'] = data['status'].value
        if 'created_at' in data:
            data['created_at'] = data['created_at'].isoformat()
        return data

    class Config:
        from_attributes = True
