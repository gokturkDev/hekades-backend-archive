import asyncio
import logging
import uuid
from typing import Optional, Union

from llama_index.core import Document
from llama_index.core.ingestion import IngestionPipeline

from ai.indexing.doc_parser.chunk_summarizer import ChunkSummarizer
from ai.indexing.doc_parser.chunk_translator import ChunkTranslator
from ai.indexing.doc_parser.page_aware_manual_splitter import PageAwareManualSplitterNodeParser
from ai.indexing.indexing_pipeline.indexing_pipeline import IndexingPipeline
from ai.indexing.utils.llama_index_utils import text_node_to_chunk
from ai.indexing.vector_index.vector_index import VectorIndex
from ai.models.standard_llm import StandardLLM
from business.entity.source.source_chunk import SourceChunk, ChunkType
from business.entity.source.source_entity import SourceEntity

logger = logging.getLogger("hekades")


class AnnotatedTextFileIndexingPipeline(IndexingPipeline):
    def __init__(self, vector_index: VectorIndex, ai_model: StandardLLM):
        super().__init__(vector_index=vector_index)
        self.ingestion_pipeline = IngestionPipeline(
            transformations=[
                PageAwareManualSplitterNodeParser(),
                ChunkTranslator(ai_model=ai_model),
                ChunkSummarizer(ai_model=ai_model)
            ]
        )

    def run(self, source: SourceEntity):
        text = source.file.file_io.read().decode("utf-8")
        document = Document(text=text, metadata={"source_id": source.info.id})

        nodes = self.ingestion_pipeline.run(documents=[document], show_progress=True)
        chunks = [text_node_to_chunk(node) for node in nodes]
        chunks.insert(0, self._get_table_of_contents_chunk(text, source))
        self._add_tags_to_chunks(text, chunks)

        return self.vector_index.index_chunks(chunks)

    @classmethod
    def _add_tags_to_chunks(cls, text: str, chunks: list[SourceChunk]):
        start_marker = "{{!TAG!}}"
        end_marker = "{{!ENDTAG!}}"

        tags = cls._get_text_between_markers(start_marker.format(number=1), end_marker.format(number=1),
                                             text).split("\n")

        for chunk in chunks:
            chunk.tags = tags

    @classmethod
    def _get_table_of_contents_chunk(cls, text: str, source: SourceEntity):
        start_marker = "{!TOC!}"
        end_marker = "{!ENDTOC!}"

        toc_text = cls._get_text_between_markers(start_marker, end_marker, text)

        if toc_text:
            return SourceChunk(
                source_id=source.info.id,
                chunk_id=str(uuid.uuid4()),
                content=toc_text,
                summary=toc_text,
                chunk_type=ChunkType.TABLE_OF_CONTENTS,
                metadata={
                    "page_numbers": [1]
                }
            )
        else:
            raise ValueError("No TOC!")

    @staticmethod
    def _get_text_between_markers(start_marker: str, end_marker: Optional[str], text: str) -> Union[str, None]:
        start = text.find(start_marker)
        if start == -1:
            logger.warning(f"Marker {start_marker} hasn't been found in the text, proceeding without...")
            return
        start += len(start_marker)

        if not end_marker:
            return text[start:].strip()
        end = text.find(end_marker)
        if end == -1:
            logger.error(f"Start marker {start_marker} has been found but end marker {end_marker} hasn't, aborting")
            raise ValueError("Abort")
        return text[start:end].strip()
