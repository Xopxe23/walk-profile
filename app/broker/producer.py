import json
import logging
from typing import Optional

from aiokafka import AIOKafkaProducer

from app.config.main import settings
from app.logger import get_logger
from app.utils import custom_serializer


class KafkaProducer:
    likes_topic: str
    matches_topic: str
    _instance: Optional["KafkaProducer"] = None

    def __new__(cls, kafka_url: str, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, kafka_url: str, logger: logging.Logger):
        if not hasattr(self, 'producer'):
            self.producer = AIOKafkaProducer(bootstrap_servers=kafka_url)
            self.logger = logger
            self.likes_topic = "likes"
            self.matches_topic = "matches"

    async def start(self) -> None:
        await self.producer.start()

    async def stop(self) -> None:
        if self.producer:
            await self.producer.stop()
            self.producer = None

    async def sent_message(self, topic: str, data: dict) -> None:
        message = json.dumps(data, default=custom_serializer)
        await self.producer.send(topic, message.encode("utf-8"))
        self.logger.info(f"Message sent to Kafka topic {topic}: {message}")


def get_kafka_producer() -> KafkaProducer:
    logger = get_logger()
    return KafkaProducer(settings.kafka.KAFKA_URL, logger)
