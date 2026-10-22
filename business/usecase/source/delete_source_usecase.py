from ai.indexing.vector_index.vector_index import VectorIndex
from business.repository.source.source_repository import SourceRepository
from business.usecase.source.use_case_with_source_repo import UsecaseWithSourceRepository


class DeleteSourceUsecase(UsecaseWithSourceRepository):

    def __init__(self, source_repo: SourceRepository, vector_index: VectorIndex):
        super().__init__(source_repo)
        self.vector_index = vector_index

    def execute(self, source_id: str):
        self._repo.delete_source(source_id)
        self.vector_index.delete_chunks_of_source(source_id)
