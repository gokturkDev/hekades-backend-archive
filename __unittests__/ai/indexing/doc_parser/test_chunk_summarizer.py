from unittest.mock import Mock

import pytest
from llama_index.core.schema import TextNode

from ai.indexing.doc_parser.chunk_summarizer import ChunkSummarizer
from ai.models.standard_llm import StandardLLM
import nest_asyncio

nest_asyncio.apply()


@pytest.fixture
def mock_ai_model():
    mock = Mock(spec=StandardLLM)
    mock.get_response.return_value = "This is an english summary with a lot of common english words."
    return mock


@pytest.mark.asyncio
async def test_chunk_summarizer(mock_ai_model):
    nodes = [
        TextNode(
            text="Suppp"
        ),
        TextNode(
            text="dawgg"
        )
    ]

    chunk_summarizer = ChunkSummarizer(
        ai_model=mock_ai_model
    )

    chunk_summarizer._parse_nodes(nodes)

    for node in nodes:
        assert node.metadata["hekades_summary"]
