from celery import Celery

from app.config.main import settings

celery = Celery(
    "tasks",
    broker=settings.redis.REDIS_URL,
    include=["app.tasks.tasks"]
)
