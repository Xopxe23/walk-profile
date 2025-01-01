from typing import Annotated

from fastapi import APIRouter, Depends

from app.exceptions.auth import InvalidTelegramDataException
from app.interfaces.services import ProfilesServiceInterface
from app.schemas.users import AccessTokenOutSchema, TelegramUserInSchema
from app.services.profiles import get_profiles_service

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post("/token")
async def telegram_auth(
        telegram_user_data: TelegramUserInSchema,
        profiles_service: Annotated[ProfilesServiceInterface, Depends(get_profiles_service)],
) -> AccessTokenOutSchema:
    if not profiles_service.verify_telegram_hash(telegram_user_data):
        raise InvalidTelegramDataException

    user = await profiles_service.get_user_by_telegram_id(telegram_user_data.id)
    if not user:
        user = await profiles_service.create_user_with_telegram_user_data(telegram_user_data)

    access_token = profiles_service.create_access_token(user.user_id)

    return AccessTokenOutSchema(
        access_token=access_token,
    )
