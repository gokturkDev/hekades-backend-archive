import asyncio
from datetime import datetime
from time import sleep
from typing import Optional
from unittest.mock import Mock
from uuid import uuid4

import pytest
import trio

from ai.indexing.vector_index.vector_index import VectorIndex
from ai.models.standard_llm import StandardLLM
from ai.retrieval.fusion.fusion_retriever import SubQueries, FusionRetriever
from business.entity.source.source_chunk import SourceChunk


@pytest.mark.asyncio
async def test_fus_retriever():
    mock_ai_model = Mock(spec=StandardLLM)
    mock_vector_index = Mock(spec=VectorIndex)
    retriever = FusionRetriever(
        ai_model=mock_ai_model,
        vector_index=mock_vector_index
    )

    async def get_mock_queries(query, prompt, base_model):
        return SubQueries(sub_queries=["query1", "query2", "query3", "query4", "query5"])

    def mock_hybrid_search(query: str, top_k: int, allowed_docs_ids: Optional[list[str]] = None):
        sleep(1)
        return [SourceChunk(source_id="source_id", chunk_id=str(uuid4()), content="content", metadata={}, score=1) for _
                in range(top_k)]

    mock_ai_model.get_response_with_response_model = get_mock_queries
    mock_vector_index.hybrid_search = mock_hybrid_search

    before_time = datetime.now()
    await retriever.retrieve("Some Query")
    after_time = datetime.now()
    delta = after_time - before_time

    assert delta.seconds <= 1.1
