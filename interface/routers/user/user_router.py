from typing import Union

import inject
from fastapi import APIRouter, Depends, UploadFile, Form

from business.entity.user.user_entity import UserEntity
from interface.auth.auth import get_current_active_user
from main.dependency_container import DepContainer

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/")
def get_user(user: UserEntity = Depends(get_current_active_user)):
    return user.model_dump_json()


@router.put("/")
def update_user(profile_picture: UploadFile = None,
                full_name: Union[str, None] = Form(None),
                user: UserEntity = Depends(get_current_active_user)):
    if profile_picture is not None:
        inject.instance(DepContainer).user_repo.update_profile_picture(user.email, profile_picture.file.read())
    if full_name is not None:
        inject.instance(DepContainer).user_repo.update(user.email, full_name)
    user = inject.instance(DepContainer).user_repo.get(user.email)
    return user.model_dump_json()
