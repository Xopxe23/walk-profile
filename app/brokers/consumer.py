import json
import logging
from typing import AsyncGenerator, Optional

from aiokafka import AIOKafkaConsumer, ConsumerRecord
from aiokafka.errors import KafkaError

from app.configs.main import settings
from app.exceptions.auth import MatchExistsException
from app.interfaces.services import ProfilesServiceInterface
from app.logger import get_logger
from app.models.likes import LikeStatusEnum
from app.schemas.matches import MatchCreateSchema
from app.services.profile import get_profiles_service


class KafkaConsumer:
    _instance: Optional["KafkaConsumer"] = None

    def __new__(cls, kafka_url: str, group_id: str, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
            self, kafka_url: str, group_id: str, profiles_service: ProfilesServiceInterface, logger: logging.Logger
    ):
        if not hasattr(self, 'consumer'):
            self.consumer = AIOKafkaConsumer(
                bootstrap_servers=kafka_url,
                group_id=group_id,
                enable_auto_commit=True
            )
            self.profiles_service = profiles_service
            self.logger = logger
            self.subscribed_topics = []

    async def start(self) -> None:
        await self.consumer.start()

    async def stop(self) -> None:
        if self.consumer:
            await self.consumer.stop()
            self.consumer = None

    async def subscribe(self, topics: list[str]) -> None:
        self.subscribed_topics.extend(topics)
        self.consumer.subscribe(topics)

    async def consume_messages(self) -> AsyncGenerator[ConsumerRecord, None]:
        """Consume messages from subscribed topics."""
        try:
            async for message in self.consumer:
                yield message
        except (KafkaError, json.JSONDecodeError, UnicodeDecodeError) as e:
            self.logger.error(f"Error while consuming messages: {e}")

    async def process_messages(self) -> None:
        """Обрабатываем сообщения из Kafka."""
        async for message in self.consume_messages():
            if message.topic == "likes":
                data = self._decode_message(message)
                user_id = data["user_id"]
                liked_user_id = data["liked_user_id"]
                like_exists = await self.profiles_service.check_mutual_like(user_id, liked_user_id)
                if like_exists:
                    try:
                        match_data = MatchCreateSchema(
                            user1_id=user_id,
                            user2_id=liked_user_id,
                        )
                        await self.profiles_service.create_match(match_data)
                        await self.profiles_service.update_like_status(data["like_id"], LikeStatusEnum.match)
                        await self.profiles_service.update_like_status(like_exists.like_id, LikeStatusEnum.match)
                    except MatchExistsException as e:
                        self.logger.error(f"Failed to create match: {e}")

    def _decode_message(self, message: ConsumerRecord) -> dict:
        try:
            data = json.loads(message.value.decode("utf-8"))
            self.logger.info(f"Received message from topic {message.topic}: {data}")
            return data
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode JSON: {e} | Raw message: {message.value}")


def get_kafka_consumer() -> KafkaConsumer:
    profiles_service = get_profiles_service()
    logger = get_logger()

    return KafkaConsumer(
        kafka_url=settings.kafka.KAFKA_URL,
        group_id="profiles",
        profiles_service=profiles_service,
        logger=logger,
    )
