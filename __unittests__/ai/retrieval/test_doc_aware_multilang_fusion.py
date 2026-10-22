from datetime import datetime
from time import sleep
from typing import Optional
from unittest.mock import Mock
from uuid import uuid4

import pytest
import trio

from ai.indexing.vector_index.vector_index import VectorIndex
from ai.models.standard_llm import StandardLLM
from ai.retrieval.fusion.doc_aware_multilang_fusion_retriever import DocAwareMultilangFusionRetriever, \
    SelectedGuidelines
from ai.retrieval.fusion.fusion_retriever import SubQueries
from business.entity.source.source_chunk import SourceChunk


@pytest.mark.asyncio
async def test_fus_retriever():
    mock_ai_model = Mock(spec=StandardLLM)
    mock_vector_index = Mock(spec=VectorIndex)
    retriever = DocAwareMultilangFusionRetriever(
        ai_model=mock_ai_model,
        vector_index=mock_vector_index
    )

    def get_mock_queries(query, prompt, base_model):
        if base_model == SelectedGuidelines:
            return SelectedGuidelines(guideline_ids=[str(uuid4()) for _ in range(10)])
        return SubQueries(sub_queries=["query1", "query2", "query3", "query4", "query5"])

    def mock_hybrid_search(query: str, top_k: int, allowed_docs_ids: Optional[list[str]] = None):
        sleep(1)
        return [SourceChunk("source_id", str(uuid4()), "content", {}, score=1) for _ in range(top_k)]

    def mock_toc_search():
        return [SourceChunk("source_id", str(uuid4()), "content", {}, score=1) for _ in range(5)]

    mock_ai_model.get_response_with_response_model = get_mock_queries
    mock_vector_index.hybrid_search = mock_hybrid_search
    mock_vector_index.get_all_toc_chunks = mock_toc_search

    before_time = datetime.now()
    chunks = trio.run(retriever.retrieve, "Some Query")
    after_time = datetime.now()
    delta = after_time - before_time

    assert delta.seconds <= 1.1
    assert len(chunks) == 55  # 10(eng+tur)*5 + 5 (turkish query)
