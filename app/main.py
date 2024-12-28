import asyncio
import os
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from app.api.auth import router as auth_router
from app.api.profile import router as profile_router
from app.brokers.consumer import get_kafka_consumer
from app.brokers.producer import get_kafka_producer
from app.logger import get_logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger = get_logger()
    kafka_producer = get_kafka_producer()
    await kafka_producer.start()
    logger.info("Kafka Producer initialized.")

    kafka_consumer = get_kafka_consumer()
    await kafka_consumer.start()
    await kafka_consumer.subscribe(["likes", "matches"])
    _ = asyncio.create_task(kafka_consumer.process_messages())
    logger.info("Kafka Consumer initialized.")

    yield

    await kafka_producer.stop()
    logger.info("Kafka Producer stopped.")

    await kafka_consumer.stop()
    logger.info("Kafka Consumer stopped.")


app = FastAPI(
    title="WALK Profile",
    lifespan=lifespan,
)

app.include_router(auth_router)
app.include_router(profile_router)


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", reload=True, port=8001,
    )
