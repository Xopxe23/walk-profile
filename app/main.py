import os
import sys
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from app.auth.router import router as auth_router

from app.logger import get_logger

from app.broker.consumer import get_kafka_consumer
from app.broker.producer import get_kafka_producer

logger = get_logger()


async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    kafka_producer = get_kafka_producer()
    await kafka_producer.start()
    logger.info("Kafka Producer initialized.")

    kafka_consumer = get_kafka_consumer()
    await kafka_consumer.start()
    await kafka_consumer.subscribe(["likes", "matches"])
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


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", reload=True,
    )
