from typing import List

from business.entity.source.source_entity import SourceEntity
from business.entity.source.source_info import SourceInfo
from business.repository.source.source_repository import SourceRepository
from core.utils.file import File
from data.repository.source.source_display_file_repository.source_display_file_repository import \
    SourceDisplayFileRepository
from data.repository.source.source_info_repository.source_info_repository import SourceInfoRepository


class FacadeSourceRepository(SourceRepository):

    def __init__(self, source_info_repo: SourceInfoRepository,
                 source_display_file_repository: SourceDisplayFileRepository):
        self.source_info_repo = source_info_repo
        self.source_display_file_repository = source_display_file_repository

    def get_source_info_from_id(self, source_id: str) -> SourceInfo:
        return self.source_info_repo.get_source_info(source_id)

    def get_all_sources_info(self) -> List[SourceInfo]:
        return self.source_info_repo.get_all_sources_info()

    def get_source_display_file_from_id(self, source_id: str) -> File:
        return self.source_display_file_repository.get_source_file(source_id=source_id)

    def add_source(self, source: SourceEntity):
        self.source_info_repo.add_source_info(info=source.info)
        self.source_display_file_repository.add_source_file(source_id=source.info.id, file=source.file)

    def update_source_info(self, source_info: SourceInfo):
        self.source_info_repo.update_source_info(info=source_info)

    def delete_source(self, source_id: str):
        self.source_info_repo.delete_source_info(source_id=source_id)
        self.source_display_file_repository.delete_source_file(source_id=source_id)
