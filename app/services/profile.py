import hashlib
import hmac
import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional

import jwt

from app.broker.producer import get_kafka_producer
from app.config.main import settings
from app.filters.base import BaseFilter
from app.interfaces.brokers import KafkaProducerInterface
from app.interfaces.repositories import LikesRepositoryInterface, MatchesRepositoryInterface, UsersRepositoryInterface
from app.logger import get_logger
from app.models.likes import LikeStatusEnum
from app.repositories.likes import get_likes_repository
from app.repositories.matches import get_matches_repository
from app.repositories.users import get_users_repository
from app.schemas.likes import LikeCreateSchema, LikeSchema
from app.schemas.matches import MatchCreateSchema
from app.schemas.users import TelegramUserInSchema, UserSchema, UserUpdateSchema


class ProfilesService:
    def __init__(
            self,
            users_repository: UsersRepositoryInterface,
            likes_repository: LikesRepositoryInterface,
            matches_repository: MatchesRepositoryInterface,
            kafka_producer: KafkaProducerInterface,
            logger: logging.Logger,
    ):
        self.users_repository = users_repository
        self.likes_repository = likes_repository
        self.matches_repository = matches_repository
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
        result = await self.users_repository.get_user_by_telegram_id(telegram_id)
        return result

    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[UserSchema]:
        result = await self.users_repository.get_user_by_id(user_id)
        return result

    async def update_user_info(self, user_id: uuid.UUID, user_data: UserUpdateSchema) -> Optional[UserSchema]:
        return await self.users_repository.update_user_info(user_id, user_data)

    async def create_user_with_telegram_user_data(self, user_data: TelegramUserInSchema) -> UserSchema:
        user = await self.users_repository.create_user_with_telegram_user_data(user_data)
        return user

    async def create_like(self, user_id: uuid.UUID, like_data: LikeCreateSchema) -> LikeSchema:
        like = await self.likes_repository.create_like(user_id, like_data)
        await self.kafka_producer.sent_message(self.kafka_producer.likes_topic, like.dict())
        return like

    async def get_my_likes(self, user_id: uuid.UUID, filters: BaseFilter) -> list[LikeSchema]:
        likes = await self.likes_repository.get_my_likes(user_id, filters)
        return likes

    async def check_mutual_like(self, user_id: uuid.UUID, liked_user_id: uuid.UUID) -> Optional[LikeSchema]:
        like_exists = await self.likes_repository.check_mutual_like(user_id, liked_user_id)
        return like_exists

    async def update_like_status(self, like_id: uuid.UUID, status: LikeStatusEnum) -> Optional[LikeSchema]:
        like = await self.likes_repository.update_like_status(like_id, status)
        return like

    async def create_match(self, match_data: MatchCreateSchema) -> None:
        match = await self.matches_repository.create_match(match_data)
        await self.kafka_producer.sent_message(self.kafka_producer.matches_topic, match.dict())
        return match


def get_profiles_service() -> ProfilesService:
    users_repository = get_users_repository()
    likes_repository = get_likes_repository()
    matches_repository = get_matches_repository()
    kafka_producer = get_kafka_producer()
    logger = get_logger()

    return ProfilesService(
        users_repository=users_repository,
        likes_repository=likes_repository,
        matches_repository=matches_repository,
        kafka_producer=kafka_producer,
        logger=logger,
    )
