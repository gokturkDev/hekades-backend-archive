from abc import ABC, abstractmethod
from typing import List

from business.entity.source.source_entity import SourceEntity
from business.entity.source.source_info import SourceInfo
from business.repository.base_repository import BaseRepository
from core.utils.file import File


class SourceRepository(BaseRepository, ABC):

    @abstractmethod
    def get_source_info_from_id(self, source_id: str) -> SourceInfo:
        pass

    @abstractmethod
    def update_source_info(self, source_info: SourceInfo):
        pass

    @abstractmethod
    def get_source_display_file_from_id(self, source_id: str) -> File:
        pass

    @abstractmethod
    def get_all_sources_info(self) -> List[SourceInfo]:
        pass

    @abstractmethod
    def add_source(self, source: SourceEntity):
        pass

    @abstractmethod
    def delete_source(self, source_id: str):
        pass
