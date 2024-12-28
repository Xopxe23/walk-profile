from app.configs.base import BaseConfig


class SecretsConfig(BaseConfig):
    TELEGRAM_SECRET: str
    JWT_SECRET: str
    ALGORITHM: str
