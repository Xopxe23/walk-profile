import uuid
from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional, Union

from aiobotocore.client import AioBaseClient
from fastapi import UploadFile

from app.filters.base import BaseFilter
from app.models.likes import LikeStatusEnum
from app.schemas.likes import LikeCreateSchema, LikeSchema
from app.schemas.matches import MatchCreateSchema, MatchSchema
from app.schemas.users import (
    TelegramUserInSchema,
    UserDocumentSchema,
    UserSchema,
    UserUpdatePhotoSchema,
    UserUpdateSchema,
)


class ProfilesPostgresRepositoryInterface(ABC):
    @abstractmethod
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[UserSchema]:
        raise NotImplementedError

    @abstractmethod
    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[UserSchema]:
        raise NotImplementedError

    @abstractmethod
    async def update_user_info(
            self, user_id: uuid.UUID, user_data: Union[UserUpdateSchema, UserUpdatePhotoSchema]
    ) -> Optional[UserSchema]:
        raise NotImplementedError

    @abstractmethod
    async def create_user_with_telegram_user_data(self, user_data: TelegramUserInSchema) -> UserSchema:
        raise NotImplementedError

    @abstractmethod
    async def create_like(self, user_id: uuid.UUID, like_data: LikeCreateSchema) -> LikeSchema:
        raise NotImplementedError

    @abstractmethod
    async def get_my_likes(self, user_id: uuid.UUID, filters: BaseFilter) -> list[LikeSchema]:
        raise NotImplementedError

    @abstractmethod
    async def check_mutual_like(self, user_id: uuid.UUID, liked_user_id: uuid.UUID) -> Optional[LikeSchema]:
        raise NotImplementedError

    @abstractmethod
    async def update_like_status(self, like_id: uuid.UUID, status: LikeStatusEnum) -> Optional[LikeSchema]:
        raise NotImplementedError

    @abstractmethod
    async def create_match(self, match_data: MatchCreateSchema) -> MatchSchema:
        raise NotImplementedError


class ProfilesElasticRepositoryInterface(ABC):
    @abstractmethod
    async def update_user_document(self, user: UserDocumentSchema) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_users_queue(self, user: UserSchema) -> list[str]:
        raise NotImplementedError


class ProfileQueuesRedisRepositoryInterface(ABC):
    @abstractmethod
    async def connect(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_users_queue(self, user_id: str) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    async def pop_from_queue(self, user_id: str) -> Optional[str]:
        raise NotImplementedError

    @abstractmethod
    async def add_to_queue(self, user_id: str, target_user_ids: list[str]) -> None:
        raise NotImplementedError


class ProfilesS3RepositoryInterface(ABC):
    @abstractmethod
    async def upload_file(self, file: UploadFile, user_uuid: uuid.UUID) -> str:
        pass

    @abstractmethod
    async def get_client(self) -> AsyncGenerator[AioBaseClient, None]:
        pass
