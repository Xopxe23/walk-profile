from typing import Optional

import redis.asyncio as redis

from app.configs.main import settings
from app.interfaces.repositories import ProfileQueuesRedisRepositoryInterface


class ProfileQueuesRedisRepository(ProfileQueuesRedisRepositoryInterface):
    _instance: Optional["ProfileQueuesRedisRepository"] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.redis = redis.from_url(
            settings.redis.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )

    async def connect(self):
        await self.redis.ping()

    async def close(self):
        if self.redis:
            await self.redis.close()

    async def get_users_queue(self, user_id: str) -> list:
        queue = await self.redis.lrange(user_id, 0, -1)
        return queue if queue else []

    async def pop_from_queue(self, user_id: str) -> Optional[str]:
        return await self.redis.lpop(user_id)

    async def add_to_queue(self, user_id: str, target_user_ids: list[str]) -> None:
        if target_user_ids:
            await self.redis.rpush(user_id, *target_user_ids)


def get_profile_queues_redis_repository() -> ProfileQueuesRedisRepository:
    return ProfileQueuesRedisRepository()
