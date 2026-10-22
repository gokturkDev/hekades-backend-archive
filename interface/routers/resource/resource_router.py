import logging
from io import BytesIO, StringIO

from fastapi import APIRouter, UploadFile, Depends
from fastapi.responses import StreamingResponse, Response

from business.entity.user.user_entity import UserEntity
from core.utils.file import File
from interface.auth.auth import get_current_admin_user
import inject
import csv
from main.dependency_container import DepContainer

router = APIRouter(prefix="/resource", tags=["resource"])
logger = logging.getLogger("hekades")


@router.post("/summarize")
def summarize_resource(resource_file: UploadFile, admin_user: UserEntity = Depends(get_current_admin_user)):
    file_content = resource_file.file.read()
    file_io = BytesIO(file_content)
    file = File(resource_file.filename, file_io)
    summarizer = inject.instance(DepContainer).resource_summarizer
    summary = summarizer.summarize_resource(file)

    return StreamingResponse(summary, media_type="text/plain")


@router.post("/tag")
def upload_tags(file: UploadFile, admin_user: UserEntity = Depends(get_current_admin_user)):
    file_content = file.file.read().decode("utf-8-sig")
    reader = csv.reader(StringIO(file_content), delimiter=";")
    tags = []
    skip = True
    for row in reader:
        if skip:
            skip = False
            continue
        tags.extend([tag.strip() for tag in row if tag.strip()])

    return Response(content="\n".join(tags).encode("utf-8"), media_type="text/csv")
