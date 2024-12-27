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

    class Config:
        from_attributes = True
