import logging
from typing import List, Optional

from weaviate.classes.query import Filter
from weaviate.classes.query import HybridFusion, MetadataQuery
from weaviate.client import WeaviateClient

from ai.indexing.embedder.embedder import Embedder
from ai.indexing.vector_index.vector_index import VectorIndex
from business.entity.source.source_chunk import SourceChunk, ChunkType
from data.helpers.weaviate_utils_mixin import WeaviateUtilsMixin
from data.indexing.vector_index.weaviate_collections import create_source_chunk_collection

logger = logging.getLogger("hekades")


class WeaviateVectorIndex(VectorIndex, WeaviateUtilsMixin):
    def __init__(self, client: WeaviateClient, embedder: Embedder):
        super().__init__(embedder)
        self.client = client
        self.collection_name = "source_chunks"

        if not self.client.collections.exists(self.collection_name):
            create_source_chunk_collection(self.client)

        self.source_chunk_collection = self.client.collections.get("source_chunks")

    def index_chunks(self, chunks: list[SourceChunk]):
        logger.info("Embedding chunks...")
        content_vectors = self.embedder.embed([chunk.content for chunk in chunks if chunk.content is not None],
                                              verbose=True)
        summary_vectors = self.embedder.embed([chunk.summary for chunk in chunks if chunk.summary is not None],
                                              verbose=True)

        with self.source_chunk_collection.batch.dynamic() as batch:
            for i, chunk in enumerate(chunks):
                batch.add_object(
                    properties={
                        "source_id": chunk.source_id,
                        "content": chunk.content,
                        "summary": chunk.summary,
                        "chunk_type": chunk.chunk_type.value,
                        "metadata": chunk.metadata,
                        "tags": chunk.tags
                    },
                    vector={
                        "content": content_vectors[i],
                        "summary": summary_vectors[i],
                    },
                    uuid=chunk.chunk_id
                )

    # Add more experiemental query strats here, directly on the vector indexx impl.
    # Since they are coupled with the data store/schemas, it makes sense to keep them here.
    def semantic_search(self, query: str, top_k: int, allowed_docs_ids: Optional[list[str]] = None) -> List[
        SourceChunk]:
        def near_text_query():
            filters = []
            if allowed_docs_ids is not None:
                filters.append(Filter.by_property("source_id").contains_any(allowed_docs_ids))
            filters.append(Filter.by_property("chunk_type").equal(ChunkType.CONTENT.value))

            query_vector = self.embedder.embed([query])[0]

            return self.source_chunk_collection.query.near_vector(
                near_vector=query_vector,
                filters=(
                    Filter.all_of(filters)
                ),
                limit=top_k,
                target_vector="summary",  # Specify the target vector for named vector collections
                return_metadata=MetadataQuery(score=True),
            )

        response = self._query_with_retry(near_text_query)

        chunks = []
        for o in response.objects:
            chunk = self._response_to_chunk(o)
            chunks.append(chunk)
        return chunks

    def hybrid_search(self, query: str, top_k: int, allowed_docs_ids: Optional[list[str]] = None, alpha: float = None) -> List[
        SourceChunk]:
        if len(allowed_docs_ids) == 0:
            return []

        def hybrid_query():
            filters = []
            if allowed_docs_ids is not None:
                filters.append(Filter.by_property("source_id").contains_any(allowed_docs_ids))
            filters.append(Filter.by_property("chunk_type").equal(ChunkType.CONTENT.value))

            query_vector = self.embedder.embed([query])[0]

            return self.source_chunk_collection.query.hybrid(
                query=query,
                vector=query_vector,
                filters=(
                    Filter.all_of(filters)
                ),
                limit=top_k,
                alpha=0.82 if not alpha else alpha,  # Weight of the vector similarity
                target_vector="summary",  # Specify the target vector for named vector collections
                fusion_type=HybridFusion.RELATIVE_SCORE,
                return_metadata=MetadataQuery(score=True),
            )

        response = self._query_with_retry(hybrid_query)

        chunks = []
        for o in response.objects:
            chunk = self._response_to_chunk(o)
            chunks.append(chunk)
        return chunks

    def get_chunks_of_source(self, source_id: str) -> List[SourceChunk]:
        def update_query():
            return self.source_chunk_collection.query.fetch_objects(
                filters=Filter.by_property("source_id").equal(source_id),
                include_vector=True,
                limit=1000
            )

        response = self._query_with_retry(update_query)
        chunks = []
        for o in response.objects:
            chunks.append(self._response_to_chunk(o))
        return chunks

    def get_all_toc_chunks(self) -> List[SourceChunk]:
        def toc_query():
            return self.source_chunk_collection.query.fetch_objects(
                filters=Filter.by_property("chunk_type").equal(ChunkType.TABLE_OF_CONTENTS.value),
                limit=1000
            )

        result = self._query_with_retry(toc_query)
        return [self._response_to_chunk(o) for o in result.objects]

    def tag_toc_search(self, tags: list[str]) -> List[SourceChunk]:
        def tag_query():
            if not len(tags):
                return []
            return self.source_chunk_collection.query.fetch_objects(
                filters=Filter.by_property("tags").contains_any(tags) & Filter.by_property(
                    "chunk_type").equal(ChunkType.TABLE_OF_CONTENTS.value),
                limit=1000
            ).objects

        result = self._query_with_retry(tag_query)

        return [self._response_to_chunk(o) for o in result]

    def update_chunk_content(self, source_id: str, chunk_id: str, content: str):
        def update_query():
            return self.source_chunk_collection.data.update(
                uuid=chunk_id,
                properties={
                    "content": content
                },
                vector={"content": self.embedder.embed([content])[0]}
            )

        result = self._query_with_retry(update_query)

    def delete_chunks_of_source(self, source_id: str):
        def delete_query():
            return self.source_chunk_collection.data.delete_many(
                where=Filter.by_property("source_id").equal(source_id)
            )

        result = self._query_with_retry(delete_query)
        if result.failed > 0:
            logger.error(f"Failed to delete {result.failed} chunks ")

    @staticmethod
    def _response_to_chunk(obj) -> SourceChunk:
        props = obj.properties

        return SourceChunk(
            source_id=str(props["source_id"]),
            chunk_id=str(obj.uuid),
            content=props["content"],
            summary=props["summary"],
            chunk_type=ChunkType(str(props["chunk_type"])),
            content_embedding=obj.vector["content"] if 'content' in obj.vector else None,
            metadata=props["metadata"] if 'metadata' in props else None,
            tags=props["tags"],
            score=obj.metadata.score
        )
