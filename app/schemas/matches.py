import datetime
import uuid
from typing import Optional

from pydantic import BaseModel

from app.models.matches import MatchStatusEnum


class MatchCreateSchema(BaseModel):
    user1_id: uuid.UUID
    user2_id: uuid.UUID


class MatchSchema(BaseModel):
    match_id: uuid.UUID
    user1_id: uuid.UUID
    user2_id: uuid.UUID
    status: MatchStatusEnum
    created_at: Optional[datetime.datetime]

    def dict(self, **kwargs):
        data = super().dict(**kwargs)
        if 'match_id' in data:
            data['match_id'] = str(data['match_id'])
        if 'user1_id' in data:
            data['user1_id'] = str(data['user1_id'])
        if 'user2_id' in data:
            data['user2_id'] = str(data['user2_id'])
        if 'status' in data:
            data['status'] = data['status'].value
        if 'created_at' in data:
            data['created_at'] = data['created_at'].isoformat()
        return data

    class Config:
        from_attributes = True
