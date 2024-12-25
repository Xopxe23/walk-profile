import uuid
from typing import Optional, Protocol

import jwt
from fastapi import APIRouter, Depends
from fastapi.security import APIKeyHeader

from app.auth.filters import BaseFilter
from app.auth.schemas import (
    AccessTokenOutSchema,
    LikeCreateSchema,
    LikeSchema,
    TelegramUserInSchema,
    UserSchema,
    UserUpdateSchema,
)
from app.auth.services import get_auth_service
from app.config.main import settings
from app.exceptions.auth import InvalidTelegramDataException, InvalidTokenException, UserNotFoundException
from app.exceptions.common import NotFoundException

router = APIRouter(
    prefix="/profile",
)

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)


def get_current_user_id(token: str = Depends(api_key_header)) -> uuid.UUID:
    try:
        payload = jwt.decode(token, settings.secret.JWT_SECRET, algorithms=[settings.secret.ALGORITHM])
        user_id: uuid.UUID = payload.get("sub")
        if user_id is None:
            raise InvalidTokenException
        return user_id
    except jwt.PyJWTError:
        raise InvalidTokenException


class AuthServiceInterface(Protocol):
    def verify_telegram_hash(self, user_data: TelegramUserInSchema) -> bool:
        ...

    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[UserSchema]:
        ...

    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[UserSchema]:
        ...

    async def update_user_info(self, user_id: uuid.UUID, user_data: UserUpdateSchema) -> UserSchema:
        ...

    def create_access_token(self, user_id: int) -> str:
        ...

    async def create_user_with_telegram_user_data(self, user_data: TelegramUserInSchema) -> UserSchema:
        ...

    async def create_like(self, user_id: uuid.UUID, like_data: LikeCreateSchema) -> LikeSchema:
        ...

    async def get_my_likes(self, user_id: uuid.UUID, filters: BaseFilter) -> list[LikeSchema]:
        ...


@router.post("/token", tags=["Auth"])
async def telegram_auth(
        telegram_user_data: TelegramUserInSchema,
        auth_service: AuthServiceInterface = Depends(get_auth_service),
) -> AccessTokenOutSchema:
    if not auth_service.verify_telegram_hash(telegram_user_data):
        raise InvalidTelegramDataException

    user = await auth_service.get_user_by_telegram_id(telegram_user_data.id)
    if not user:
        user = await auth_service.create_user_with_telegram_user_data(telegram_user_data)

    access_token = auth_service.create_access_token(user.user_id)

    return AccessTokenOutSchema(
        access_token=access_token,
    )


@router.get("/me", tags=["Profile"])
async def get_me(
        user_id: uuid.UUID = Depends(get_current_user_id),
        auth_service: AuthServiceInterface = Depends(get_auth_service),
) -> UserSchema:
    user = await auth_service.get_user_by_id(user_id)
    return user


@router.put("/me", tags=["Profile"])
async def update_user_data(
        user_data: UserUpdateSchema,
        user_id: uuid.UUID = Depends(get_current_user_id),
        auth_service: AuthServiceInterface = Depends(get_auth_service),
) -> UserSchema:
    user = await auth_service.update_user_info(user_id, user_data)
    if not user:
        raise NotFoundException
    return user


@router.post("/like", tags=["Like"])
async def like_profile(
        like_data: LikeCreateSchema,
        user_id: uuid.UUID = Depends(get_current_user_id),
        auth_service: AuthServiceInterface = Depends(get_auth_service),
) -> LikeSchema:
    user_exists = await auth_service.get_user_by_id(like_data.liked_user_id)
    if not user_exists:
        raise UserNotFoundException
    like = await auth_service.create_like(user_id, like_data)
    return like


@router.get("/likes", tags=["Like"])
async def get_my_likes(
        user_id: uuid.UUID = Depends(get_current_user_id),
        filters: BaseFilter = Depends(),
        auth_service: AuthServiceInterface = Depends(get_auth_service),
) -> list[LikeSchema]:
    likes = await auth_service.get_my_likes(user_id, filters)
    return likes
