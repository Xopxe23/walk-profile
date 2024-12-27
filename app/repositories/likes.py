import uuid
from typing import Optional

from sqlalchemy import and_, desc, select, update
from sqlalchemy.exc import IntegrityError

from app.database import async_session_maker
from app.exceptions.auth import LikeExistsException
from app.filters.base import BaseFilter
from app.models.likes import Likes, LikeStatusEnum
from app.schemas.likes import LikeCreateSchema, LikeSchema


class LikesRepository:

    def __init__(self):
        self.model = Likes

    async def create_like(self, user_id: uuid.UUID, like_data: LikeCreateSchema) -> LikeSchema:
        like = self.model(
            user_id=user_id,
            **like_data.dict(),
        )
        async with async_session_maker() as session:
            try:
                session.add(like)
                await session.commit()
            except IntegrityError:
                raise LikeExistsException
            await session.refresh(like)
        return LikeSchema.model_validate(like)

    async def get_my_likes(self, user_id: uuid.UUID, filters: BaseFilter) -> list[LikeSchema]:
        query = (
            select(self.model)
            .where(and_(
                self.model.liked_user_id == user_id,
                self.model.status != LikeStatusEnum.match,
            ))
            .order_by(desc(self.model.created_at))
            .offset(filters.offset)
            .limit(filters.limit)
        )
        async with async_session_maker() as session:
            result = await session.execute(query)
        likes = [LikeSchema.model_validate(like) for like in result.scalars()]
        return likes

    async def check_mutual_like(self, user_id: uuid.UUID, liked_user_id: uuid.UUID) -> Optional[LikeSchema]:
        query = (
            select(self.model)
            .where(and_(self.model.user_id == liked_user_id, self.model.liked_user_id == user_id))
        )
        async with async_session_maker() as session:
            result = await session.execute(query)
        like = result.scalar_one_or_none()
        if not like:
            return None
        return LikeSchema.model_validate(like)

    async def update_like_status(self, like_id: uuid.UUID, status: LikeStatusEnum) -> Optional[LikeSchema]:
        stmt = (
            update(self.model)
            .where(self.model.like_id == like_id)
            .values(status=status)
            .returning(self.model)
        )
        async with async_session_maker() as session:
            result = await session.execute(stmt)
            await session.commit()
        like = result.scalar_one_or_none()
        if not like:
            return None
        return LikeSchema.model_validate(like)


def get_likes_repository() -> LikesRepository:
    return LikesRepository()
