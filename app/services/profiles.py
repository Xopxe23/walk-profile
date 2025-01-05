import asyncio
import hashlib
import hmac
import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional, Union

import jwt
from fastapi import UploadFile

from app.brokers.producer import get_kafka_producer
from app.configs.main import settings
from app.filters.base import BaseFilter
from app.interfaces.brokers import KafkaProducerInterface
from app.interfaces.repositories import (
    ProfileQueuesRedisRepositoryInterface,
    ProfilesElasticRepositoryInterface,
    ProfilesPostgresRepositoryInterface,
    ProfilesS3RepositoryInterface,
)
from app.interfaces.services import ProfilesServiceInterface
from app.logger import get_logger
from app.models.likes import LikeStatusEnum
from app.repositories.profiles_es import get_profiles_es_repository
from app.repositories.profiles_pg import get_profiles_pg_repository
from app.repositories.profiles_redis import get_profile_queues_redis_repository
from app.repositories.profiles_s3 import get_profiles_s3_repository
from app.schemas.likes import LikeCreateSchema, LikeSchema
from app.schemas.matches import MatchCreateSchema
from app.schemas.users import TelegramUserInSchema, UserSchema, UserUpdatePhotoSchema, UserUpdateSchema


class ProfilesService(ProfilesServiceInterface):
    def __init__(
            self,
            profiles_pg_repository: ProfilesPostgresRepositoryInterface,
            profiles_elastic_repository: ProfilesElasticRepositoryInterface,
            profiles_s3_repository: ProfilesS3RepositoryInterface,
            profile_queues_redis_repository: ProfileQueuesRedisRepositoryInterface,
            kafka_producer: KafkaProducerInterface,
            logger: logging.Logger,
    ):
        self.profiles_pg_repository = profiles_pg_repository
        self.profiles_elastic_repository = profiles_elastic_repository
        self.profiles_s3_repository = profiles_s3_repository
        self.profile_queues_redis_repository = profile_queues_redis_repository
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
        user = await self.profiles_pg_repository.get_user_by_telegram_id(telegram_id)
        return user

    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[UserSchema]:
        user = await self.profiles_pg_repository.get_user_by_id(user_id)
        return user

    async def update_user_info(
            self, user_id: uuid.UUID, user_data: Union[UserUpdateSchema, UserUpdatePhotoSchema]
    ) -> Optional[UserSchema]:
        user = await self.profiles_pg_repository.update_user_info(user_id, user_data)
        _ = asyncio.create_task(self.update_user_document(user))
        return user

    async def create_user_with_telegram_user_data(self, user_data: TelegramUserInSchema) -> UserSchema:
        user = await self.profiles_pg_repository.create_user_with_telegram_user_data(user_data)
        _ = asyncio.create_task(self.update_user_document(user))
        return user

    async def create_like(self, user_id: uuid.UUID, like_data: LikeCreateSchema) -> LikeSchema:
        like = await self.profiles_pg_repository.create_like(user_id, like_data)
        await self.kafka_producer.sent_message(self.kafka_producer.likes_topic, like.dict())
        self.logger.info(f"Message sent to Kafka topic {self.kafka_producer.likes_topic}: {like.dict()}")
        return like

    async def get_my_likes(self, user_id: uuid.UUID, filters: BaseFilter) -> list[LikeSchema]:
        likes = await self.profiles_pg_repository.get_my_likes(user_id, filters)
        tasks = [
            asyncio.create_task(self.profiles_pg_repository.update_like_status(like.like_id, LikeStatusEnum.seen))
            for like in likes if like.status == LikeStatusEnum.new
        ]
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    like_id = likes[i].id
                    self.logger.error(f"Ошибка при обновлении лайка с ID {like_id}: {result}")
        return likes

    async def check_mutual_like(self, user_id: uuid.UUID, liked_user_id: uuid.UUID) -> Optional[LikeSchema]:
        like_exists = await self.profiles_pg_repository.check_mutual_like(user_id, liked_user_id)
        return like_exists

    async def update_like_status(self, like_id: uuid.UUID, status: LikeStatusEnum) -> Optional[LikeSchema]:
        like = await self.profiles_pg_repository.update_like_status(like_id, status)
        return like

    async def create_match(self, match_data: MatchCreateSchema) -> None:
        match = await self.profiles_pg_repository.create_match(match_data)
        await self.kafka_producer.sent_message(self.kafka_producer.matches_topic, match.dict())
        self.logger.info(f"Message sent to Kafka topic {self.kafka_producer.matches_topic}: {match.dict()}")
        return match

    async def update_user_document(self, user: UserSchema) -> None:
        await self.profiles_elastic_repository.update_user_document(user)
        self.logger.info(f"User data with ID {user.user_id} successfully updated in Elasticsearch.")

    async def get_user_for_action(self, user_id: uuid.UUID) -> Optional[UserSchema]:
        user_for_action = await self.profile_queues_redis_repository.pop_from_queue(user_id)
        return user_for_action

    async def add_users_queue(self, user: UserSchema) -> None:
        users_ids_queue = await self._get_users_queue(user)
        await self.profile_queues_redis_repository.add_to_queue(str(user.user_id), users_ids_queue)

    async def upload_photo(self, user_uuid: uuid.UUID, file: UploadFile) -> str:
        return await self.profiles_s3_repository.upload_file(file, user_uuid)

    async def _get_users_queue(self, user: UserSchema) -> list[str]:
        return await self.profiles_elastic_repository.get_users_queue(user)


def get_profiles_service() -> ProfilesService:
    profiles_pg_repository = get_profiles_pg_repository()
    profiles_elastic_repository = get_profiles_es_repository()
    profiles_s3_repository = get_profiles_s3_repository()
    profile_queues_redis_repository = get_profile_queues_redis_repository()
    kafka_producer = get_kafka_producer()
    logger = get_logger()

    return ProfilesService(
        profiles_pg_repository=profiles_pg_repository,
        profiles_elastic_repository=profiles_elastic_repository,
        profiles_s3_repository=profiles_s3_repository,
        profile_queues_redis_repository=profile_queues_redis_repository,
        kafka_producer=kafka_producer,
        logger=logger,
    )
