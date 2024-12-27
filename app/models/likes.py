import datetime
import enum
import uuid

from sqlalchemy import TIMESTAMP, Enum, ForeignKey, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class LikeStatusEnum(enum.Enum):
    new = "new"
    seen = "seen"
    match = "match"


class Likes(Base):
    __tablename__ = "likes"

    like_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.user_id"))
    liked_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.user_id"))
    status: Mapped[LikeStatusEnum] = mapped_column(Enum(LikeStatusEnum), default=LikeStatusEnum.new)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, server_default=text("NOW()"))

    __table_args__ = (UniqueConstraint('user_id', 'liked_user_id', name='_user_liked_user_uc'),)
