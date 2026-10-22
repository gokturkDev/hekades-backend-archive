from abc import ABC, abstractmethod

from core.utils.file import File


class ChunkResourceRepository(ABC):

    @abstractmethod
    def store_chunk_resource(self, source_id: str, chunk_id: str, resource: File):
        pass

    @abstractmethod
    def get_chunk_resource(self, source_id: str, chunk_id: str) -> File:
        pass

    @abstractmethod
    def get_chunk_resource_url(self, source_id: str, chunk_id: str) -> str:
        pass

    @abstractmethod
    def delete_all_chunk_resources_of_source(self, source_id: str):
        pass
    
    @abstractmethod
    def delete_chunk_resource(self, source_id: str, chunk_id: str):
        pass
