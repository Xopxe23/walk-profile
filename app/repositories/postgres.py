import uuid
from typing import Optional

from sqlalchemy import and_, desc, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.database import get_async_session_maker
from app.exceptions.auth import LikeExistsException, MatchExistsException
from app.filters.base import BaseFilter
from app.interfaces.repositories import ProfilesPostgresRepositoryInterface
from app.models.likes import Likes, LikeStatusEnum
from app.models.matches import Matches
from app.models.users import Users
from app.schemas.likes import LikeCreateSchema, LikeSchema
from app.schemas.matches import MatchCreateSchema, MatchSchema
from app.schemas.users import TelegramUserInSchema, UserSchema, UserUpdateSchema


class ProfilesPostgresRepository(ProfilesPostgresRepositoryInterface):

    def __init__(self, session_maker: async_sessionmaker[AsyncSession]):
        self.session_maker = session_maker
        self.users_table = Users
        self.likes_table = Likes
        self.matches_table = Matches

    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[UserSchema]:
        query = (
            select(self.users_table)
            .where(self.users_table.telegram_id == telegram_id)
        )
        async with self.session_maker() as session:
            result = await session.execute(query)
        user = result.scalar_one_or_none()
        return UserSchema.model_validate(user) if user else None

    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[UserSchema]:
        query = select(self.users_table).where(self.users_table.user_id == user_id)
        async with self.session_maker() as session:
            result = await session.execute(query)
        user = result.scalar_one_or_none()
        if user is None:
            return None
        return UserSchema.model_validate(user)

    async def update_user_info(self, user_id: uuid.UUID, user_data: UserUpdateSchema) -> Optional[UserSchema]:
        query = (
            update(self.users_table)
            .where(self.users_table.user_id == user_id)
            .values(**user_data.dict(exclude_none=True)).returning(self.users_table)
        )
        async with self.session_maker() as session:
            result = await session.execute(query)
            await session.commit()
        user = result.scalar_one_or_none()
        return UserSchema.model_validate(user) if user else None

    async def create_user_with_telegram_user_data(self, user_data: TelegramUserInSchema) -> UserSchema:
        user = self.users_table(
            telegram_id=user_data.id,
            name=user_data.first_name,
        )
        async with self.session_maker() as session:
            session.add(user)
            await session.commit()
            await session.refresh(user)
        return UserSchema.model_validate(user)

    async def create_like(self, user_id: uuid.UUID, like_data: LikeCreateSchema) -> LikeSchema:
        like = self.likes_table(
            user_id=user_id,
            **like_data.dict(),
        )
        async with self.session_maker() as session:
            try:
                session.add(like)
                await session.commit()
            except IntegrityError:
                raise LikeExistsException
            await session.refresh(like)
        return LikeSchema.model_validate(like)

    async def get_my_likes(self, user_id: uuid.UUID, filters: BaseFilter) -> list[LikeSchema]:
        query = (
            select(self.likes_table)
            .where(and_(
                self.likes_table.liked_user_id == user_id,
                self.likes_table.status != LikeStatusEnum.match,
            ))
            .order_by(desc(self.likes_table.created_at))
            .offset(filters.offset)
            .limit(filters.limit)
        )
        async with self.session_maker() as session:
            result = await session.execute(query)
        likes = [LikeSchema.model_validate(like) for like in result.scalars()]
        return likes

    async def check_mutual_like(self, user_id: uuid.UUID, liked_user_id: uuid.UUID) -> Optional[LikeSchema]:
        query = (
            select(self.likes_table)
            .where(and_(self.likes_table.user_id == liked_user_id, self.likes_table.liked_user_id == user_id))
        )
        async with self.session_maker() as session:
            result = await session.execute(query)
        like = result.scalar_one_or_none()
        if not like:
            return None
        return LikeSchema.model_validate(like)

    async def update_like_status(self, like_id: uuid.UUID, status: LikeStatusEnum) -> Optional[LikeSchema]:
        stmt = (
            update(self.likes_table)
            .where(self.likes_table.like_id == like_id)
            .values(status=status)
            .returning(self.likes_table)
        )
        async with self.session_maker() as session:
            result = await session.execute(stmt)
            await session.commit()
        like = result.scalar_one_or_none()
        if not like:
            return None
        return LikeSchema.model_validate(like)

    async def create_match(self, match_data: MatchCreateSchema) -> MatchSchema:
        match = self.matches_table(
            **match_data.dict()
        )
        async with self.session_maker() as session:
            try:
                session.add(match)
                await session.commit()
            except IntegrityError:
                raise MatchExistsException
        return MatchSchema.model_validate(match)


def get_profiles_pg_repository() -> ProfilesPostgresRepository:
    session_maker = get_async_session_maker()
    return ProfilesPostgresRepository(
        session_maker=session_maker,
    )
