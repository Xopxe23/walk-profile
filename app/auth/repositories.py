from typing import AsyncGenerator, Optional

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.auth.schemas import TelegramUserInSchema, UserSchema
from app.database import get_async_session


class UserRepository:
    def __init__(
            self,
            session: AsyncSession,
    ):
        self.user_table = User
        self.session = session

    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[UserSchema]:
        query = select(self.user_table).where(self.user_table.telegram_id == telegram_id)
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()
        if user is None:
            return None
        return UserSchema.model_validate(user)

    async def create_user_with_telegram_user_data(self, user_data: TelegramUserInSchema) -> UserSchema:
        user = self.user_table(
            telegram_id=user_data.id,
            name=user_data.first_name,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return UserSchema.model_validate(user)


def get_user_repository(session: AsyncSession = Depends(get_async_session)) -> AsyncGenerator[UserRepository, None]:
    yield UserRepository(
        session=session,
    )
