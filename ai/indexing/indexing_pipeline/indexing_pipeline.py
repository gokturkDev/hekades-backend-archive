from abc import ABC, abstractmethod

from ai.indexing.vector_index.vector_index import VectorIndex
from business.entity.source.source_entity import SourceEntity


class IndexingPipeline(ABC):
    vector_index: VectorIndex

    def __init__(self, vector_index: VectorIndex):
        self.vector_index = vector_index

    @abstractmethod
    def run(self, source: SourceEntity):
        pass
