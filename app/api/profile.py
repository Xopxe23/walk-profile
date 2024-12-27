import uuid

from fastapi import APIRouter, Depends

from app.exceptions.auth import UserNotFoundException
from app.exceptions.common import NotFoundException
from app.filters.base import BaseFilter
from app.interfaces.services import ProfilesServiceInterface
from app.schemas.likes import LikeCreateSchema, LikeSchema
from app.schemas.users import UserSchema, UserUpdateSchema
from app.services.profile import get_profiles_service
from app.utils import get_current_user_id

router = APIRouter(
    prefix="/profile",
    tags=["Profile"]
)


@router.get("/me")
async def get_me(
        user_id: uuid.UUID = Depends(get_current_user_id),
        auth_service: ProfilesServiceInterface = Depends(get_profiles_service),
) -> UserSchema:
    user = await auth_service.get_user_by_id(user_id)
    return user


@router.put("/me")
async def update_user_data(
        user_data: UserUpdateSchema,
        user_id: uuid.UUID = Depends(get_current_user_id),
        auth_service: ProfilesServiceInterface = Depends(get_profiles_service),
) -> UserSchema:
    user = await auth_service.update_user_info(user_id, user_data)
    if not user:
        raise NotFoundException
    return user


@router.post("/like")
async def like_profile(
        like_data: LikeCreateSchema,
        user_id: uuid.UUID = Depends(get_current_user_id),
        auth_service: ProfilesServiceInterface = Depends(get_profiles_service),
) -> LikeSchema:
    user_exists = await auth_service.get_user_by_id(like_data.liked_user_id)
    if not user_exists:
        raise UserNotFoundException
    like = await auth_service.create_like(user_id, like_data)
    return like


@router.get("/likes")
async def get_my_likes(
        user_id: uuid.UUID = Depends(get_current_user_id),
        filters: BaseFilter = Depends(),
        auth_service: ProfilesServiceInterface = Depends(get_profiles_service),
) -> list[LikeSchema]:
    likes = await auth_service.get_my_likes(user_id, filters)
    return likes
