from abc import ABC, abstractmethod
from typing import List, Optional

from ai.indexing.embedder.embedder import Embedder
from business.entity.source.source_chunk import SourceChunk


class VectorIndex(ABC):

    @abstractmethod
    def __init__(self, embedder: Embedder):
        self.embedder = embedder

    @abstractmethod
    def index_chunks(self, chunks: list[SourceChunk]):
        pass

    @abstractmethod
    def get_chunks_of_source(self, source_id: str) -> List[SourceChunk]:
        pass

    @abstractmethod
    def get_all_toc_chunks(self) -> List[SourceChunk]:
        pass

    @abstractmethod
    def tag_toc_search(self, tags: list[str]) -> List[SourceChunk]:
        pass

    @abstractmethod
    def delete_chunks_of_source(self, source_id: str):
        pass

    @abstractmethod
    def update_chunk_content(self, source_id: str, chunk_id: str, content: str):
        pass

    @abstractmethod
    def semantic_search(self, query: str, top_k: int, allowed_docs_ids: Optional[list[str]] = None) -> List[
        SourceChunk]:
        pass

    @abstractmethod
    def hybrid_search(self, query: str, top_k: int, allowed_docs_ids: Optional[list[str]] = None, alpha: float = None) -> List[
        SourceChunk]:
        pass
