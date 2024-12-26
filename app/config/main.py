from app.config.kafka import KafkaConfig
from app.config.postgres import PostgresConfig
from app.config.redis import RedisConfig
from app.config.secret import SecretsConfig


class AppSettings:
    def __init__(self):
        self.postgres = PostgresConfig()
        self.secret = SecretsConfig()
        self.redis = RedisConfig()
        self.kafka = KafkaConfig()


settings = AppSettings()
