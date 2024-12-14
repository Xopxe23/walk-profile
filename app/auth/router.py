from typing import Optional, Protocol

from fastapi import APIRouter, Depends

from app.auth.schemas import AccessTokenOutSchema, TelegramUserInSchema, UserSchema
from app.auth.services import get_auth_service
from app.exceptions.auth import InvalidTelegramDataException

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


class AuthServiceInterface(Protocol):
    def verify_telegram_hash(self, user_data: TelegramUserInSchema) -> bool:
        ...

    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[UserSchema]:
        ...

    def create_access_token(self, user_id: int) -> str:
        ...

    async def create_user_with_telegram_user_data(self, user_data: TelegramUserInSchema) -> UserSchema:
        ...


@router.post("/token")
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
