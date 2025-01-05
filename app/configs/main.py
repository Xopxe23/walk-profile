from app.configs.elastic import ElasticConfig
from app.configs.kafka import KafkaConfig
from app.configs.postgres import PostgresConfig
from app.configs.redis import RedisConfig
from app.configs.s3 import S3Config
from app.configs.secret import SecretsConfig


class AppSettings:
    def __init__(self):
        self.postgres = PostgresConfig()
        self.secret = SecretsConfig()
        self.redis = RedisConfig()
        self.kafka = KafkaConfig()
        self.elastic = ElasticConfig()
        self.s3 = S3Config()


settings = AppSettings()
