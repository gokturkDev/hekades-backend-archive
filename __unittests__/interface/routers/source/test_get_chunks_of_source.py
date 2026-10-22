import pytest

from __test_utils__.mock_dependency_container import MockDepContainer
from __unittests__.interface.routers.test_router import TestRouter
from business.entity.source.source_chunk import SourceChunk


class TestGetChunksOfSource(TestRouter):

    def setup_method(self):
        super().setup_method()
        MockDepContainer.vector_index.get_chunks_of_source.return_value = [
            SourceChunk(
                source_id="123",
                chunk_id="abc-123",
                content="Hello World",
                metadata={}
            ),
            SourceChunk(
                source_id="123",
                chunk_id="def-456",
                content="Goodbye World",
                metadata={}
            )
        ]

    @pytest.mark.asyncio
    def test_get_chunks_of_source(self):
        response = self.client.get(
            "/source/123/all"
        )

        serialized_chunks = response.json()["chunks"]

        MockDepContainer.vector_index.get_chunks_of_source.assert_called_once_with("123")
        assert len(serialized_chunks) == 2
        for chunk in serialized_chunks:
            assert chunk["source_id"] == "123"
            assert chunk["chunk_id"] == "abc-123" or chunk["chunk_id"] == "def-456"
            assert chunk["content"] == "Hello World" or chunk["content"] == "Goodbye World"
