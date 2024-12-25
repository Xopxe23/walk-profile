import datetime
import uuid

from sqlalchemy import JSON, TIMESTAMP, Enum, ForeignKey, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.utils import LikeStatus, UserSex, Zodiac, uuid_pk


class User(Base):
    __tablename__ = "base_user"

    user_id: Mapped[uuid_pk]
    telegram_id: Mapped[int]
    name: Mapped[str]
    age: Mapped[int] = mapped_column(nullable=True)
    sex: Mapped[UserSex] = mapped_column(Enum(UserSex), nullable=True)
    bio: Mapped[str] = mapped_column(nullable=True)
    interests: Mapped[list] = mapped_column(JSON, nullable=True)
    city: Mapped[str] = mapped_column(nullable=True)
    zodiac: Mapped[Zodiac] = mapped_column(Enum(Zodiac), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, server_default=text("NOW()"))


class Like(Base):
    __tablename__ = "like"

    like_id: Mapped[uuid_pk]
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("base_user.user_id"))
    liked_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("base_user.user_id"))
    status: Mapped[LikeStatus] = mapped_column(Enum(LikeStatus), default=LikeStatus.new)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, server_default=text("NOW()"))

    __table_args__ = (UniqueConstraint('user_id', 'liked_user_id', name='_user_liked_user_uc'),)


class Match(Base):
    __tablename__ = "match"

    match_id: Mapped[uuid_pk]
    user1_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("base_user.user_id"))
    user2_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("base_user.user_id"))
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, server_default=text("NOW()"))

    __table_args__ = (
        # Добавление уникального индекса на пару (user1_id, user2_id)
        UniqueConstraint('user1_id', 'user2_id', name='uq_user_pair'),
        UniqueConstraint('user2_id', 'user1_id', name='uq_user_pair_reversed')
    )
