import json
import logging
from typing import AsyncGenerator, Optional

from aiokafka import AIOKafkaConsumer

from app.config.main import settings
from app.logger import get_logger


class KafkaConsumer:
    _instance: Optional["KafkaConsumer"] = None

    def __new__(cls, kafka_url: str, group_id: str, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, kafka_url: str, group_id: str, logger: logging.Logger):
        if not hasattr(self, 'consumer'):
            self.consumer = AIOKafkaConsumer(
                bootstrap_servers=kafka_url,
                group_id=group_id,
                enable_auto_commit=True
            )
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

    async def consume_messages(self) -> AsyncGenerator[dict, None]:
        """Consume messages from subscribed topics."""
        try:
            async for message in self.consumer:
                yield {
                    "topic": message.topic,
                    "partition": message.partition,
                    "offset": message.offset,
                    "key": message.key.decode("utf-8") if message.key else None,
                    "value": json.loads(message.value.decode("utf-8")),
                    "timestamp": message.timestamp,
                }
        except Exception as e:
            print(f"Error while consuming messages: {e}")


def get_kafka_consumer() -> KafkaConsumer:
    logger = get_logger()
    return KafkaConsumer(settings.kafka.KAFKA_URL, "profile", logger)
