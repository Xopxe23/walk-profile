import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, UploadFile

from app.exceptions.common import NotFoundException
from app.exceptions.profiles import UserNotFoundException
from app.filters.base import BaseFilter
from app.interfaces.services import ProfilesServiceInterface
from app.schemas.likes import LikeCreateSchema, LikeSchema
from app.schemas.users import UserSchema, UserUpdatePhotoSchema, UserUpdateSchema
from app.services.profiles import get_profiles_service
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


@router.get("/get_user_for_action")
async def get_user_for_action(
        user_id: uuid.UUID = Depends(get_current_user_id),
        auth_service: ProfilesServiceInterface = Depends(get_profiles_service),
) -> Optional[UserSchema]:
    user_id_for_action = await auth_service.get_user_for_action(user_id)
    if not user_id_for_action:
        user = await auth_service.get_user_by_id(user_id)
        await auth_service.add_users_queue(user)
        user_id_for_action = await auth_service.get_user_for_action(user_id)
    user_for_action = await auth_service.get_user_by_id(user_id_for_action)
    return user_for_action


@router.post("/update_photo")
async def update_photo(
        file: UploadFile = File(...),
        user_id: uuid.UUID = Depends(get_current_user_id),
        auth_service: ProfilesServiceInterface = Depends(get_profiles_service),
) -> Optional[UserSchema]:
    photo_url = await auth_service.upload_photo(user_id, file)
    user = await auth_service.update_user_info(user_id, UserUpdatePhotoSchema(photo_url=photo_url))
    return user
