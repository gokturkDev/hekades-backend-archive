from abc import abstractmethod, ABC
from typing import Callable

from ai.indexing.vector_index.vector_index import VectorIndex
from business.entity.source.source_entity import SourceEntity
from business.entity.source.source_info import SourceInfo


class SourceIndexer(ABC):

    def __init__(self, vector_index: VectorIndex):
        self.vector_index = vector_index

    @abstractmethod
    def index_source(self, source: SourceEntity,
                     finished_callback: Callable[[SourceInfo], None] = None):
        pass
