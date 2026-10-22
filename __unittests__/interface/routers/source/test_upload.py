import tempfile

import pytest

from __test_utils__.mock_dependency_container import MockDepContainer
from __test_utils__.test_file_factory import TestFileFactory
from __unittests__.interface.routers.test_router import TestRouter
from business.entity.source.source_entity import SourceEntity


class TestUpload(TestRouter):

    def setup_method(self):
        def save_file_content_side_effect(source: SourceEntity):
            # Save the file content
            MockDepContainer.source_repo.saved_file_content = source.file.file_io.read()

        super().setup_method()
        MockDepContainer.source_repo.add_source.side_effect = save_file_content_side_effect

    def test_temp_file(self):
        fp = tempfile.TemporaryFile()
        content = b'Hello world!'
        fp.write(content)
        fp.seek(0)
        assert content == fp.read()
        fp.close()

    @pytest.mark.asyncio
    async def test_should_upload_file(self):
        test_content = b'Hello world!'
        test_source_name = "Lord of the rings"
        test_file = TestFileFactory.create_test_file_from_string(test_file_name="test.txt", test_content=test_content)

        response = await self._query_upload_source_endpoint(
            file=test_file,
            name=test_source_name
        )
        assert response.status_code == 200

        mock_source_repo = MockDepContainer.source_repo
        mock_source_repo.add_source.assert_called_once()
        mock_source_indexer = MockDepContainer.source_indexer
        mock_source_indexer.index_source.assert_called_once()

        assert mock_source_repo.saved_file_content == test_content

    async def _query_upload_source_endpoint(self, file, name):
        return self.client.post(
            "/source",
            data={
                "source_name": name
            },
            files={
                "index_file": (file.filename, file.file_io),
                "display_file": (file.filename, file.file_io)
            },

        )
