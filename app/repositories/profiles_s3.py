import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from aiobotocore.client import AioBaseClient
from aiobotocore.session import get_session
from fastapi import UploadFile

from app.configs.main import settings
from app.interfaces.repositories import ProfilesS3RepositoryInterface


class ProfilesS3Repository(ProfilesS3RepositoryInterface):
    def __init__(
            self,
            access_key: str,
            secret_key: str,
            endpoint_url: str,
            bucket_name: str,
    ):
        self.config = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "endpoint_url": endpoint_url,
        }
        self.bucket_name = bucket_name
        self.session = get_session()

    @asynccontextmanager
    async def get_client(self) -> AsyncGenerator[AioBaseClient, None]:
        async with self.session.create_client("s3", **self.config) as client:
            yield client

    async def upload_file(
            self,
            file: UploadFile,
            user_uuid: uuid.UUID
    ) -> str:
        file_extension = file.filename.split('.')[-1]
        object_name = f"profiles/{user_uuid}.{file_extension}"
        async with self.get_client() as client:
            await client.put_object(
                Bucket=self.bucket_name,
                Key=object_name,
                Body=file.file,
            )
        url = f"{settings.s3.S3_BUCKET_URL}/{object_name}"
        return url


def get_profiles_s3_repository() -> ProfilesS3Repository:
    return ProfilesS3Repository(
        access_key=settings.s3.S3_ACCESS_KEY,
        secret_key=settings.s3.S3_SECRET_KEY,
        endpoint_url=settings.s3.S3_ENDPOINT_URL,
        bucket_name=settings.s3.S3_BUCKET_NAME,
    )
