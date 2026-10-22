from abc import ABC, abstractmethod

from core.utils.file import File


class SourceDisplayFileRepository(ABC):
    @abstractmethod
    def add_source_file(self, source_id: str, file: File):
        pass

    @abstractmethod
    def delete_source_file(self, source_id: str):
        pass

    @abstractmethod
    def get_source_file(self, source_id: str) -> File:
        pass
