import uuid
from typing import AsyncGenerator, Optional

from fastapi import Depends
from sqlalchemy import and_, desc, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.filters import BaseFilter
from app.auth.models import Like, Match, User
from app.auth.schemas import (
    LikeCreateSchema,
    LikeSchema,
    MatchCreateSchema,
    MatchSchema,
    TelegramUserInSchema,
    UserSchema,
    UserUpdateSchema,
)
from app.database import get_async_session
from app.exceptions.auth import LikeExistsException, MatchExistsException
from app.utils import LikeStatus


class UserRepository:
    def __init__(
            self,
            session: AsyncSession,
    ):
        self.user_table = User
        self.like_table = Like
        self.match_table = Match
        self.session = session

    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[UserSchema]:
        query = select(self.user_table).where(self.user_table.telegram_id == telegram_id)
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()
        return UserSchema.model_validate(user) if user else None

    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[UserSchema]:
        query = select(self.user_table).where(self.user_table.user_id == user_id)
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()
        if user is None:
            return None
        return UserSchema.model_validate(user)

    async def update_user_info(self, user_id: uuid.UUID, user_data: UserUpdateSchema) -> Optional[UserSchema]:
        query = (update(self.user_table).where(self.user_table.user_id == user_id)
                 .values(**user_data.dict(exclude_none=True)).returning(self.user_table))
        result = await self.session.execute(query)
        await self.session.commit()
        user = result.scalar_one_or_none()
        return UserSchema.model_validate(user) if user else None

    async def create_user_with_telegram_user_data(self, user_data: TelegramUserInSchema) -> UserSchema:
        user = self.user_table(
            telegram_id=user_data.id,
            name=user_data.first_name,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return UserSchema.model_validate(user)

    async def create_like(self, user_id: uuid.UUID, like_data: LikeCreateSchema) -> LikeSchema:
        like = self.like_table(
            user_id=user_id,
            **like_data.dict(),
        )
        try:
            self.session.add(like)
            await self.session.commit()
        except IntegrityError:
            raise LikeExistsException
        await self.session.refresh(like)
        return LikeSchema.model_validate(like)

    async def get_my_likes(self, user_id: uuid.UUID, filters: BaseFilter) -> list[LikeSchema]:
        query = (
            select(self.like_table)
            .where(and_(
                self.like_table.liked_user_id == user_id,
                self.like_table.status != LikeStatus.match,
            ))
            .order_by(desc(self.like_table.created_at))
            .offset(filters.offset)
            .limit(filters.limit)
        )
        result = await self.session.execute(query)
        likes = [LikeSchema.model_validate(like) for like in result.scalars()]
        return likes

    async def check_mutual_like(self, user_id: uuid.UUID, liked_user_id: uuid.UUID) -> bool:
        query = (
            select(self.like_table)
            .where(and_(self.like_table.user_id == user_id, self.like_table.liked_user_id == liked_user_id))
        )
        result = await self.session.execute(query)
        return True if result.scalar_one_or_none() else False

    async def create_match(self, match_data: MatchCreateSchema) -> MatchSchema:
        match = self.match_table(
            **match_data.dict()
        )
        try:
            self.session.add(match)
            await self.session.commit()
        except IntegrityError:
            raise MatchExistsException
        return MatchSchema.model_validate(match)


def get_user_repository(session: AsyncSession = Depends(get_async_session)) -> AsyncGenerator[UserRepository, None]:
    yield UserRepository(
        session=session,
    )
