import uuid
from abc import ABC, abstractmethod
from typing import Optional, Union

from fastapi import UploadFile

from app.filters.base import BaseFilter
from app.models.likes import LikeStatusEnum
from app.schemas.likes import LikeCreateSchema, LikeSchema
from app.schemas.matches import MatchCreateSchema
from app.schemas.users import TelegramUserInSchema, UserSchema, UserUpdatePhotoSchema, UserUpdateSchema


class ProfilesServiceInterface(ABC):
    @abstractmethod
    def verify_telegram_hash(self, user_data: TelegramUserInSchema) -> bool:
        raise NotImplementedError

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
    def create_access_token(self, user_id: int) -> str:
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
    async def create_match(self, match_data: MatchCreateSchema) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update_user_document(self, user: UserSchema) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_user_for_action(self, user_id: uuid.UUID) -> Optional[UserSchema]:
        raise NotImplementedError

    @abstractmethod
    async def add_users_queue(self, user: UserSchema) -> None:
        raise NotImplementedError

    @abstractmethod
    async def _get_users_queue(self, user: UserSchema) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    async def upload_photo(self, user_uuid: uuid.UUID, file: UploadFile) -> str:
        pass
