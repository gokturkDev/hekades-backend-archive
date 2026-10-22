import asyncio

from llama_index.core import Document
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SemanticSplitterNodeParser

from ai.indexing.indexing_pipeline.indexing_pipeline import IndexingPipeline
from ai.indexing.utils.llama_index_utils import text_node_to_chunk
from ai.indexing.vector_index.vector_index import VectorIndex
from business.entity.source.source_entity import SourceEntity


class TextFileIndexingPipeline(IndexingPipeline):

    def __init__(self, vector_index: VectorIndex, embedding_model: BaseEmbedding):
        super().__init__(vector_index=vector_index)
        self.ingestion_pipeline = IngestionPipeline(
            transformations=[
                SemanticSplitterNodeParser(
                    buffer_size=1, breakpoint_percentile_threshold=80, embed_model=embedding_model,
                    include_metadata=True
                )
            ]
        )

    def run(self, source: SourceEntity):
        source_file = source.file
        text = source_file.file_io.read()
        document = Document(
            text=text,
            metadata={"source_id": source.info.id}
        )
        nodes = self.ingestion_pipeline.run(documents=[document], show_progress=True)
        chunks = [text_node_to_chunk(node) for node in nodes]
        return self.vector_index.index_chunks(chunks)
