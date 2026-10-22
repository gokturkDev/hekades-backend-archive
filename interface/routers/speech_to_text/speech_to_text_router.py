import logging

import inject
from fastapi import APIRouter, UploadFile, Depends

from business.entity.user.user_entity import UserEntity
from business.usecase.speech_to_text.create_transcript import CreateTranscriptUsecase
from interface.auth.auth import get_current_active_user
from main.dependency_container import DepContainer

router = APIRouter(prefix="/speech_to_text", tags=["speech_to_text"])
logger = logging.getLogger("hekades")


@router.post("/create-transcript")
async def create_transcript(speech_file: UploadFile, user: UserEntity = Depends(get_current_active_user)):
    return await _create_transcript(speech_file)


async def _create_transcript(speech_file: UploadFile):
    usecase = CreateTranscriptUsecase(stt_repo=inject.instance(DepContainer).stt_client)
    return await usecase.execute(data=speech_file)
