import logging
from typing import Callable

from openai import OpenAI

from ai.indexing.indexing_pipeline.annotated_text_file_indexing_pipeline import AnnotatedTextFileIndexingPipeline
from ai.indexing.indexing_pipeline.pdf_file_indexing_pipeline import PDFFileIndexingPipeline
from ai.indexing.vector_index.vector_index import VectorIndex
from ai.models.standard_llm import StandardLLM
from business.ai.source_indexer import SourceIndexer as ISourceIndexer
from business.entity.source.source_entity import SourceEntity
from business.entity.source.source_info import SourceInfo, IndexingStatus
from business.repository.source.chunk_resource_repository import ChunkResourceRepository

logger = logging.getLogger("hekades")


class SourceIndexer(ISourceIndexer):

    def __init__(self, vector_index: VectorIndex, chunk_resource_repo: ChunkResourceRepository,
                 openai_client: OpenAI, ai_model: StandardLLM):
        super().__init__(vector_index=vector_index)
        self.chunk_resource_repository = chunk_resource_repo
        self.openai_client = openai_client
        self.ai_model = ai_model

    def index_source(self, source: SourceEntity, finished_callback: Callable[[SourceInfo], None] = None):
        source_file = source.file
        source_file.file_io.seek(0)

        try:
            self._run_indexing(source)
            logger.info(f"Indexing completed for source {source.info.id}")
            self._call_finished_callback(source.info, IndexingStatus.COMPLETED, finished_callback)
        except Exception as e:
            logger.error(f"Indexing failed for source {source.info.id} with error: {str(e)}")
            logger.exception(e)
            self._call_finished_callback(source.info, IndexingStatus.FAILED, finished_callback)

    def _run_indexing(self, source):
        file_extension = source.file.file_extension
        if file_extension == 'txt':
            indexing_pipeline = AnnotatedTextFileIndexingPipeline(self.vector_index, self.ai_model)
        elif file_extension == 'pdf':
            indexing_pipeline = PDFFileIndexingPipeline(self.vector_index, self.chunk_resource_repository,
                                                        self.openai_client)
        else:
            raise ValueError(f"Unsupported file extension: {file_extension}")
        indexing_pipeline.run(source)

    @staticmethod
    def _call_finished_callback(info: SourceInfo, status: IndexingStatus,
                                callback: Callable[[SourceInfo, IndexingStatus], None] = None):
        new_source_info = SourceInfo(
            status=status,
            name=info.name,
            id=info.id
        )
        if callback:
            callback(new_source_info)
