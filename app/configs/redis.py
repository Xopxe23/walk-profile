from app.configs.base import BaseConfig


class RedisConfig(BaseConfig):
    REDIS_HOST: str
    REDIS_PORT: int

    @property
    def REDIS_URL(self):
        if self.DOCKER:
            self.REDIS_HOST = "profile-redis"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"
