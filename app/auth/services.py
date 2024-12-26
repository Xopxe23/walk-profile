import hashlib
import hmac
import logging
import uuid
from datetime import datetime, timedelta
from typing import AsyncGenerator, Optional, Protocol

import jwt
from fastapi import Depends

from app.broker.producer import get_kafka_producer
from app.auth.filters import BaseFilter
from app.auth.repositories import get_user_repository
from app.auth.schemas import LikeCreateSchema, LikeSchema, TelegramUserInSchema, UserSchema, UserUpdateSchema, \
    MatchCreateSchema, MatchSchema
from app.config.main import settings
from app.logger import get_logger


class UserRepositoryInterface(Protocol):
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[UserSchema]:
        ...

    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[UserSchema]:
        ...

    async def update_user_info(self, user_id: uuid.UUID, user_data: UserUpdateSchema) -> Optional[UserSchema]:
        ...

    async def create_user_with_telegram_user_data(self, user_data: TelegramUserInSchema) -> UserSchema:
        ...

    async def create_like(self, user_id: uuid.UUID, like_data: LikeCreateSchema) -> LikeSchema:
        ...

    async def get_my_likes(self, user_id: uuid.UUID, filters: BaseFilter) -> list[LikeSchema]:
        ...

    async def check_mutual_like(self, user_id: uuid.UUID, liked_user_id: uuid.UUID) -> bool:
        ...

    async def create_match(self, match_data: MatchCreateSchema) -> MatchSchema:
        ...


class KafkaProducerInterface(Protocol):
    likes_topic: str
    matches_topic: str

    async def sent_message(self, topic: str, data: dict) -> None:
        ...


class AuthService:
    def __init__(
            self,
            user_repository: UserRepositoryInterface,
            kafka_producer: KafkaProducerInterface,
            logger: logging.Logger,
    ):
        self.user_repository = user_repository
        self.kafka_producer = kafka_producer
        self.logger = logger

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

    async def create_like(self, user_id: uuid.UUID, like_data: LikeCreateSchema) -> LikeSchema:
        like = await self.user_repository.create_like(user_id, like_data)
        await self.kafka_producer.sent_message(self.kafka_producer.likes_topic, like.dict())
        return like

    async def get_my_likes(self, user_id: uuid.UUID, filters: BaseFilter) -> list[LikeSchema]:
        likes = await self.user_repository.get_my_likes(user_id, filters)
        return likes

    async def _check_mutual_like(self, user_id: uuid.UUID, liked_user_id: uuid.UUID) -> None:
        like_exists = await self.user_repository.check_mutual_like(user_id, liked_user_id)
        if like_exists:
            await self.user_repository.create_match(MatchCreateSchema(
                user1_id=user_id,
                user2_id=liked_user_id,
            ))

    async def _create_match(self, match_data: MatchCreateSchema) -> None:
        match = await self.user_repository.create_match(match_data)
        await self.kafka_producer.sent_message(self.kafka_producer.matches_topic, match.dict())
        return match


def get_auth_service(
        kafka_producer: KafkaProducerInterface = Depends(get_kafka_producer),
        user_repository: UserRepositoryInterface = Depends(get_user_repository),
        logger: logging.Logger = Depends(get_logger),
) -> AsyncGenerator[AuthService, None]:
    yield AuthService(
        user_repository=user_repository,
        kafka_producer=kafka_producer,
        logger=logger,
    )
