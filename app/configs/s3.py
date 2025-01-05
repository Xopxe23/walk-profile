from app.configs.base import BaseConfig


class S3Config(BaseConfig):
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_ENDPOINT_URL: str
    S3_BUCKET_NAME: str
    S3_BUCKET_URL: str
