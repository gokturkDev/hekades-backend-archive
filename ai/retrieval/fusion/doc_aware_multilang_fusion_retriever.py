import asyncio
from typing import Optional, override, List

from ai.indexing.embedder.embedder import Embedder
from ai.retrieval.fusion.fusion_retriever import FusionRetriever
from ai.utils.cosine_similarity import cosine_similarity_q_docs
from business.entity.source.source_chunk import SourceChunk


class DocAwareMultilangFusionRetriever(FusionRetriever):

    def __init__(self, ai_model, vector_index, logger, embedder: Embedder, query_expansion_prompt: Optional[str] = None,
                 alpha: Optional[float] = None, rank_method: Optional[str]=None, query_scoring_prompt: Optional[str] = None):
        super().__init__(ai_model, vector_index, logger, query_expansion_prompt, alpha, rank_method, query_scoring_prompt)
        self.selected_docs_id = []
        self.embedder = embedder

    @override
    async def retrieve(self, query: str, tags: List[str], rich_query: Optional[str] = None, retrieval_queries: Optional[list[str]] = None) -> List[SourceChunk]:
        if not (len(tags)):
            toc_chunks = await asyncio.to_thread(self.vector_index.get_all_toc_chunks)
        else:
            toc_chunks = await asyncio.to_thread(self.vector_index.tag_toc_search, tags)
        self.logger.info(
            f"Found {len(toc_chunks)} documents with tags\nHere are their ids: {"\n".join(chunk.source_id for chunk in toc_chunks)}")

        for chunk in toc_chunks:
            self.selected_docs_id.append(chunk.source_id)
        chunks = await super().retrieve(query, retrieval_queries)

        sorted_chunks = sorted(chunks, key=lambda chunk: chunk.score, reverse=True)
        return sorted_chunks

    @override
    async def _get_reranked_chunks(self, queries, allowed_docs_id=None):
        return await super()._get_reranked_chunks(queries, allowed_docs_id=self.selected_docs_id)

    async def _replace_score_with_to_query_score(self, query: str, chunks: list[SourceChunk]):
        query_vector, chunk_vectors = None, None
        async with asyncio.TaskGroup() as tg:
            async def assign_qv():
                nonlocal query_vector, query
                query_vector_ls = await asyncio.to_thread(self.embedder.embed, [query], False)
                query_vector = query_vector_ls[0]

            async def assign_cv():
                nonlocal chunk_vectors, chunks
                chunk_vectors = await asyncio.to_thread(self.embedder.embed, [chunk.summary for chunk in chunks], False)

            tg.create_task(assign_qv())
            tg.create_task(assign_cv())

        cosine_scores = cosine_similarity_q_docs(query_vector, chunk_vectors)
        for score, chunk in zip(cosine_scores, chunks):
            chunk.score = score
