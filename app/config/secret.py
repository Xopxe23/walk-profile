from app.config.base import BaseConfig


class SecretsConfig(BaseConfig):
    SECRET: str
    ALGORITHM: str
