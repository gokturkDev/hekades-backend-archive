import asyncio
from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel, Field

from ai.indexing.vector_index.vector_index import VectorIndex
from ai.models.standard_llm import StandardLLM
from ai.retrieval.retriever import Retriever
from business.entity.source.source_chunk import SourceChunk

QUERY_EXTRACTION_PROMPT = """
You are given a reasoning about formulating new queries for a question.
Your task is to extract the final queries as is and put them in the query_list.
ONLY EXTRACT THE FINAL QUERIES AS IS! THIS IS EXTREMELY IMPORTANT!
"""

CHUNK_CLASSIFIER = """
# Doctor's Question
{question}

# Text
{chunk}

# Instructions
Analyze the doctor's question and the below text.
If the text contains directly relevant information to the doctor's question, select Yes. Otherwise, select No.
User is strictly looking for the directly relevant information therefore be strict in selecting. 
For example, if the user is looking for viral infections then bacterial infections are indirectly relevant therefore you must select No.

"""


class YesOrNoOption(str, Enum):
    yes = "Yes"
    no = "No"


class Query(BaseModel):
    content: str
    score: int


class ScoredQueries(BaseModel):  # for scoring
    query_list: list[Query] = Field(
        default=[]
    )


class Queries(BaseModel):
    query_list: list[str]


QUERY_SCORE_EXTRACTION_PROMPT = """
Extract the queries and their score from the user message.
"""


class ResponseModel(BaseModel):
    response: YesOrNoOption


class FusionRetriever(Retriever):
    def __init__(self, ai_model: StandardLLM, vector_index: VectorIndex, logger,
                 query_expansion_prompt: Optional[str] = None, alpha: Optional[float] = None,
                 rank_method: Optional[str] = "reciprocal", query_scoring_prompt: Optional[str] = None):
        self.ai_model = ai_model
        self.vector_index = vector_index
        self.logger = logger
        self.alpha = alpha
        self.query_expansion_prompt = query_expansion_prompt
        self.query_scoring_prompt = query_scoring_prompt
        self.rank_method = rank_method
        self.top_k = 5

    async def retrieve(self, query: str, rich_query: Optional[str] = None,
                       retrieval_queries: Optional[list[SourceChunk]] = None):
        if retrieval_queries:
            queries = retrieval_queries
        elif self.query_expansion_prompt:
            query_reasoning = await self.ai_model.get_response(query, self.query_expansion_prompt)
            queries = await self.ai_model.get_response_with_response_model(query_reasoning, QUERY_EXTRACTION_PROMPT,
                                                                           Queries)
            queries = [query for query in queries.query_list if len(query.replace(" ", "")) > 0]
            queries.append(query)
        else:
            queries = [query]

        if self.query_scoring_prompt:
            queries = await self._get_top_3(query, queries)
            self.logger.info(
                f"Query and Scores:\n{"\n".join([f"Content\n{query.content}\n Score:\n{query.score}" for query in queries])}")
            queries = [query.content for query in queries]
        else:
            self.logger.info(f"Queries:\n{"\n".join([f"{query}" for query in queries])}")

        reranked_chunks = await self._get_reranked_chunks(queries)

        return reranked_chunks

    async def _classify_chunks(self, query, rich_query, reranked_chunks):
        chunk_matrix = {}
        async with asyncio.TaskGroup() as tg:
            async def classify_chunk(chunk):
                response = await self.ai_model.get_response_with_response_model(
                    prompt=CHUNK_CLASSIFIER.format(question=rich_query if rich_query else query, chunk=chunk.summary),
                    user_msg=None,
                    response_model=ResponseModel)
                chunk_matrix[chunk.chunk_id] = response.response

            for chunk in reranked_chunks:
                tg.create_task(classify_chunk(chunk))

        reranked_chunks = [chunk for chunk in reranked_chunks if chunk_matrix[chunk.chunk_id] == YesOrNoOption.yes]
        return reranked_chunks

    async def _get_top_3(self, user_message, queries):
        query_scoring = await self.ai_model.get_response(
            prompt=self.query_scoring_prompt.format(queries="\n".join(queries), question=user_message))
        query_list_model = await self.ai_model.get_response_with_response_model(prompt=QUERY_SCORE_EXTRACTION_PROMPT,
                                                                                response_model=ScoredQueries,
                                                                                user_msg=query_scoring)
        query_list = query_list_model.query_list
        query_list = sorted(query_list, key=lambda x: x.score, reverse=True)
        return query_list[:3]

    async def _get_reranked_chunks(self, queries, allowed_docs_id: Union[None, list[str]] = None):
        all_chunks = {}
        async with asyncio.TaskGroup() as tg:
            for query in queries:
                self.logger.info("Retrieving Chunks for query: " + query)
                tg.create_task(self.process_query(query, allowed_docs_id, all_chunks,
                                                  top_k=40 if self.rank_method == "reciprocal" else self.top_k))

        if self.rank_method == "reciprocal":
            reranked_chunks = self._reciprocal_rank_fusion(all_chunks, len(queries))[:20]
        else:
            reranked_chunks = []
            reranked_chunks_ids = []
            for query, chunks in all_chunks.items():
                chunks = sorted(chunks, key=lambda x: x.score, reverse=True)
                i = 0
                for chunk in chunks:
                    if chunk.chunk_id not in reranked_chunks_ids:
                        reranked_chunks.append(chunk)
                        reranked_chunks_ids.append(chunk.chunk_id)
                        i += 1
                    if i == self.top_k:
                        break

        self.logger.info(f"All chunks retrieved! Total: {len(reranked_chunks)} ")
        return reranked_chunks

    async def process_query(self, query, allowed_docs_id: Union[None, list[str]], all_chunks, top_k):
        chunks = await asyncio.to_thread(
            self.vector_index.hybrid_search, query, top_k, allowed_docs_id, self.alpha)
        all_chunks[query] = chunks

    @staticmethod
    def _reciprocal_rank_fusion(query_chunk_pair: dict[str, list[SourceChunk]], k, cutoff=0.1):
        # k is a smoothing factor
        # id -> (score, chunk)
        fused_scores = {}
        for query, chunks in query_chunk_pair.items():
            for chunk in chunks:
                if chunk.chunk_id not in fused_scores:
                    fused_scores[chunk.chunk_id] = (0, chunk)
                curr_score = fused_scores[chunk.chunk_id][0]
                new_score = 1 / ((1 - chunk.score) + k)
                fused_scores[chunk.chunk_id] = (curr_score + new_score, chunk)

        sorted_fused = sorted(fused_scores.items(), key=lambda x: x[1][0], reverse=True)

        reranked_chunks = []
        for _, chunk_tuple in sorted_fused:
            chunk = chunk_tuple[1]
            chunk.score = chunk_tuple[0]
            if chunk.score < cutoff:
                continue
            reranked_chunks.append(chunk_tuple[1])

        return reranked_chunks

    @staticmethod
    def _remove_duplicate_chunks(chunks: list[SourceChunk]) -> list[SourceChunk]:
        seen_chunk_ids = set()
        no_duplicate_chunks = []

        for chunk in chunks:
            if chunk.chunk_id in seen_chunk_ids:
                continue
            seen_chunk_ids.add(chunk.chunk_id)
            no_duplicate_chunks.append(chunk)

        return no_duplicate_chunks
