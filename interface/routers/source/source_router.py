import logging
import uuid

import inject
from fastapi import APIRouter, Form, UploadFile, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from business.entity.source.source_chunk import SourceChunk
from business.entity.source.source_info import SourceInfo
from business.entity.user.user_entity import UserEntity
from business.usecase.source.add_source_usecase import AddSourceUsecase
from business.usecase.source.delete_source_usecase import DeleteSourceUsecase
from business.usecase.source.get_sources_usecase import GetSourcesInfoUsecase
from core.utils.file import File
from interface.auth.auth import get_current_admin_user, get_current_active_user
from main.dependency_container import DepContainer

router = APIRouter(prefix="/source", tags=["source"])
logger = logging.getLogger("hekades")


@router.post("")
# FastAPI receives files with forms (multipart/form-data) therefore name needs to be passed as a form attr
def upload_source(index_file: UploadFile, display_file: UploadFile,
                  source_name: str = Form(""),
                  link: str = Form(""),
                  admin: UserEntity = Depends(get_current_admin_user)) -> str:
    logger.info(
        f"Source Upload Request Received \n Source Name: {source_name} \n Index Filename: {index_file.filename} \n Display Filename: {display_file.filename}")

    index_file = File(index_file.filename, index_file.file)
    display_file = File(display_file.filename, display_file.file)

    source_uuid = str(uuid.uuid4())
    add_usecase = AddSourceUsecase(inject.instance(DepContainer).source_repo,
                                   inject.instance(DepContainer).source_indexer)
    add_usecase.execute(source_name, link, source_uuid, index_file, display_file)
    return source_uuid


@router.delete("/{source_id}")
def delete_source(source_id: str, admin: UserEntity = Depends(get_current_admin_user)):
    delete_source_usecase = DeleteSourceUsecase(inject.instance(DepContainer).source_repo,
                                                inject.instance(DepContainer).vector_index)
    delete_source_usecase.execute(source_id)


@router.get("/all")
def get_sources(admin: UserEntity = Depends(get_current_admin_user)) -> list[SourceInfo]:
    get_sources_usecase = GetSourcesInfoUsecase(inject.instance(DepContainer).source_repo)
    source_infos = get_sources_usecase.execute()
    return source_infos


@router.get("/{source_id}")
def get_source_info(source_id: str, admin: UserEntity = Depends(get_current_active_user)) -> SourceInfo:
    return inject.instance(DepContainer).source_repo.get_source_info_from_id(source_id=source_id)


@router.get("/{source_id}/name")
def get_source_name(source_id: str, user: UserEntity = Depends(get_current_active_user)) -> str:
    info = inject.instance(DepContainer).source_repo.get_source_info_from_id(source_id)
    return info.name


@router.get("/{source_id}/file")
def get_source_file(source_id: str, user: UserEntity = Depends(get_current_active_user)) -> StreamingResponse:
    source_file = inject.instance(DepContainer).source_repo.get_source_display_file_from_id(source_id)
    return StreamingResponse(
        source_file.file_io, media_type="application/pdf"
    )


@router.get("/{source_id}/{chunk_id}/resource")
def get_chunk_resource(source_id: str, chunk_id: str,
                       admin_user: UserEntity = Depends(get_current_admin_user)) -> StreamingResponse:
    resource = inject.instance(DepContainer).chunk_resource_repo.get_chunk_resource(source_id, chunk_id)

    return StreamingResponse(
        resource.file_io, media_type="image/jpeg"
    )


# For fastapi to process the request body, it needs to be a pydantic model
class ContentModel(BaseModel):
    content: str


@router.put("/{source_id}/{chunk_id}")
def update_chunk_content(source_id: str, chunk_id: str, content: ContentModel,
                         admin_user: UserEntity = Depends(get_current_admin_user)):
    inject.instance(DepContainer).vector_index.update_chunk_content(source_id, chunk_id, content.content)


@router.get("/{source_id}/all")
def get_chunks_of_source(source_id: str, admin_user: UserEntity = Depends(get_current_admin_user)) -> list[SourceChunk]:
    chunks = inject.instance(DepContainer).vector_index.get_chunks_of_source(source_id)
    return chunks
