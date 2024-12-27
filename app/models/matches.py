import datetime
import enum
import uuid

from sqlalchemy import TIMESTAMP, Enum, ForeignKey, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class MatchStatusEnum(enum.Enum):
    new = "new"
    seen = "seen"
    deleted = "deleted"


class Matches(Base):
    __tablename__ = "matches"

    match_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user1_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.user_id"))
    user2_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.user_id"))
    status: Mapped[MatchStatusEnum] = mapped_column(Enum(MatchStatusEnum), default=MatchStatusEnum.new)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, server_default=text("NOW()"))

    __table_args__ = (
        # Добавление уникального индекса на пару (user1_id, user2_id)
        UniqueConstraint('user1_id', 'user2_id', name='uq_user_pair'),
        UniqueConstraint('user2_id', 'user1_id', name='uq_user_pair_reversed')
    )
