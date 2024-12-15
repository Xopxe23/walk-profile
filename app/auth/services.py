import hashlib
import hmac
import uuid
from datetime import datetime, timedelta
from typing import AsyncGenerator, Optional, Protocol

import jwt
from fastapi import Depends

from app.auth.repositories import get_user_repository
from app.auth.schemas import TelegramUserInSchema, UserSchema, UserUpdateSchema
from app.config.main import settings


class UserRepositoryInterface(Protocol):
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[UserSchema]:
        ...

    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[UserSchema]:
        ...

    async def update_user_info(self, user_id: uuid.UUID, user_data: UserUpdateSchema) -> Optional[UserSchema]:
        ...

    async def create_user_with_telegram_user_data(self, user_data: TelegramUserInSchema) -> UserSchema:
        ...


class AuthService:
    def __init__(
            self,
            user_repository: UserRepositoryInterface,
    ):
        self.user_repository = user_repository

    @staticmethod
    def verify_telegram_hash(user_data: TelegramUserInSchema) -> bool:
        """Проверка подписи данных для подтверждения их подлинности."""
        check_data = {key: value for key, value in user_data.dict().items() if key != 'hash'}
        check_string = '\n'.join([f"{key}={value}" for key, value in sorted(check_data.items())])

        bot_token = settings.secret.TELEGRAM_SECRET
        secret_key = hashlib.sha256(bot_token.encode()).digest()

        calculated_hash = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()

        return calculated_hash == user_data.hash

    @staticmethod
    def create_access_token(user_id: uuid.UUID) -> str:
        """Создание access token (JWT)."""
        payload = {
            "sub": str(user_id),
            "exp": datetime.utcnow() + timedelta(hours=3),
        }
        access_token = jwt.encode(payload, settings.secret.JWT_SECRET, algorithm=settings.secret.ALGORITHM)
        return access_token

    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[UserSchema]:
        result = await self.user_repository.get_user_by_telegram_id(telegram_id)
        return result

    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[UserSchema]:
        result = await self.user_repository.get_user_by_id(user_id)
        return result

    async def update_user_info(self, user_id: uuid.UUID, user_data: UserUpdateSchema) -> Optional[UserSchema]:
        return await self.user_repository.update_user_info(user_id, user_data)

    async def create_user_with_telegram_user_data(self, user_data: TelegramUserInSchema) -> UserSchema:
        user = await self.user_repository.create_user_with_telegram_user_data(user_data)
        return user


def get_auth_service(
        user_repository: UserRepositoryInterface = Depends(get_user_repository),
) -> AsyncGenerator[AuthService, None]:
    yield AuthService(
        user_repository=user_repository,
    )
