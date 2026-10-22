import pytest

from __test_utils__.mock_dependency_container import MockDepContainer
from __unittests__.interface.routers.test_router import TestRouter


class TestDeleteSource(TestRouter):

    def setup_method(self):
        super().setup_method()

    @pytest.mark.asyncio
    async def test_delete_source(self):
        test_source_id = "123"
        response = await self._query_delete_source_endpoint(test_source_id)
        assert response.status_code == 200

        MockDepContainer.source_repo.delete_source.assert_called_once_with(test_source_id)
        MockDepContainer.vector_index.delete_chunks_of_source.assert_called_once_with(test_source_id)

    async def _query_delete_source_endpoint(self, source_id):
        return self.client.delete(
            f"/source/{source_id}"
        )
