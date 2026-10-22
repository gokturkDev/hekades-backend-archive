from abc import ABC, abstractmethod
from typing import List

from business.entity.source.source_info import SourceInfo


class SourceInfoRepository(ABC):
    @abstractmethod
    def add_source_info(self, info: SourceInfo):
        pass

    @abstractmethod
    def update_source_info(self, info: SourceInfo):
        pass

    @abstractmethod
    def delete_source_info(self, source_id: str):
        pass

    @abstractmethod
    def get_all_sources_info(self) -> List[SourceInfo]:
        pass

    @abstractmethod
    def get_source_info(self, source_id: str) -> SourceInfo:
        pass
