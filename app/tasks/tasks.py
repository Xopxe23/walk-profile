import asyncio
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.repositories import UserRepository
from app.auth.schemas import MatchCreateSchema, MatchSchema
from app.database import async_session_maker
from app.tasks.celery_app import celery


@celery.task
def check_mutual_like(user_id: uuid.UUID, liked_user_id: uuid.UUID) -> Optional[MatchSchema]:
    loop = asyncio.get_event_loop()
    mutual_like = loop.run_until_complete(_check_mutual_like(user_id, liked_user_id))
    if not mutual_like:
        return None
    match_data = MatchCreateSchema(
        user1_id=user_id,
        user2_id=liked_user_id,
    )
    match = loop.run_until_complete(_create_match(match_data))
    return match


async def _check_mutual_like(user_id: uuid.UUID, liked_user_id: uuid.UUID) -> bool:
    async with _get_user_repository() as user_repo:
        like_exists = await user_repo.check_mutual_like(user_id, liked_user_id)
        return True if like_exists else False


async def _create_match(match_data: MatchCreateSchema) -> MatchSchema:
    async with _get_user_repository() as user_repo:
        match = await user_repo.create_match(match_data)
        return match


@asynccontextmanager
async def get_async_session() -> AsyncSession:
    session = async_session_maker()
    try:
        yield session
    finally:
        await session.close()


@asynccontextmanager
async def _get_user_repository() -> AsyncGenerator[UserRepository, None]:
    async with get_async_session() as session:
        user_repo = UserRepository(session)
        try:
            yield user_repo
        finally:
            await session.close()
