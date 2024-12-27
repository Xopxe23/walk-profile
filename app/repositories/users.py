import uuid
from typing import Optional

from sqlalchemy import select, update

from app.database import async_session_maker
from app.models.users import Users
from app.schemas.users import TelegramUserInSchema, UserSchema, UserUpdateSchema


class UsersRepository:

    def __init__(self):
        self.model = Users

    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[UserSchema]:
        query = (
            select(self.model)
            .where(self.model.telegram_id == telegram_id)
        )
        async with async_session_maker() as session:
            result = await session.execute(query)
        user = result.scalar_one_or_none()
        return UserSchema.model_validate(user) if user else None

    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[UserSchema]:
        query = select(self.model).where(self.model.user_id == user_id)
        async with async_session_maker() as session:
            result = await session.execute(query)
        user = result.scalar_one_or_none()
        if user is None:
            return None
        return UserSchema.model_validate(user)

    async def update_user_info(self, user_id: uuid.UUID, user_data: UserUpdateSchema) -> Optional[UserSchema]:
        query = (
            update(self.model)
            .where(self.model.user_id == user_id)
            .values(**user_data.dict(exclude_none=True)).returning(self.model)
        )
        async with async_session_maker() as session:
            result = await session.execute(query)
            await session.commit()
        user = result.scalar_one_or_none()
        return UserSchema.model_validate(user) if user else None

    async def create_user_with_telegram_user_data(self, user_data: TelegramUserInSchema) -> UserSchema:
        user = self.model(
            telegram_id=user_data.id,
            name=user_data.first_name,
        )
        async with async_session_maker() as session:
            session.add(user)
            await session.commit()
            await session.refresh(user)
        return UserSchema.model_validate(user)


def get_users_repository() -> UsersRepository:
    return UsersRepository()
