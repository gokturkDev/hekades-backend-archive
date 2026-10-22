import json

import pytest

from __test_utils__.mock_dependency_container import MockDepContainer
from __unittests__.interface.routers.test_router import TestRouter
from business.entity.source.source_info import IndexingStatus, SourceInfo


class TestGetSources(TestRouter):

    def setup_method(self):
        super().setup_method()
        MockDepContainer.source_repo.get_all_sources_info.return_value = self._get_dummy_source_infos()

    @pytest.mark.asyncio
    async def test_get_sources(self):
        response = await self._query_get_sources_endpoint()

        serialized_sources = json.loads(response.read())["sources"]

        MockDepContainer.source_repo.get_all_sources_info.assert_called_once()
        # Check if the serialized sources are correct
        assert len(serialized_sources) == 2
        for source in serialized_sources:
            assert source["id"] == "123" or source["id"] == "345"

    @staticmethod
    def _get_dummy_source_infos():
        return [
            SourceInfo(
                name="test_name",
                status=IndexingStatus.NOT_STARTED,
                id="123"
            ),
            SourceInfo(
                name="test_name",
                status=IndexingStatus.NOT_STARTED,
                id="345"
            )
        ]

    async def _query_get_sources_endpoint(self):
        return self.client.get(
            "/source/all"
        )
