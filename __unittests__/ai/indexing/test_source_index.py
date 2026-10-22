from unittest.mock import patch, Mock, ANY

import pytest

from __test_utils__.test_file_factory import TestFileFactory
from ai.indexing.source_indexer import SourceIndexer
from business.entity.source.source_entity import SourceEntity
from business.entity.source.source_info import IndexingStatus, SourceInfo


def params():
    return [
        (
            'ai.indexing.source_indexer.AnnotatedTextFileIndexingPipeline',
            TestFileFactory.create_test_file_from_string(
                "test.txt", b"test content"
            )
        ),
        (
            'ai.indexing.source_indexer.PDFFileIndexingPipeline',
            TestFileFactory.create_test_file_from_string(
                "test.pdf", b"test content"
            )
        )
    ]


@pytest.mark.parametrize('pipeline,file', params())
class TestSourceIndex:
    def test_calls_correct_pipeline(self, pipeline, file):
        with patch(pipeline) as mock_pipeline:
            source_entity = SourceEntity(info=Mock(), file=file)
            source_indexer = SourceIndexer(vector_index=Mock(), openai_client=Mock(), chunk_resource_repo=Mock())
            source_indexer.index_source(source_entity)

            mock_pipeline.return_value.run.assert_called_once()

    def test_callback_on_success(self, pipeline, file):
        with patch(pipeline):
            source_entity = SourceEntity(info=Mock(), file=file)
            source_indexer = SourceIndexer(vector_index=Mock(), openai_client=Mock(), chunk_resource_repo=Mock())

            callback = Mock()
            source_indexer.index_source(source_entity, finished_callback=callback)

            callback.assert_called_once_with(
                SourceInfo(
                    id=ANY,
                    type=ANY,
                    name=ANY,
                    status=IndexingStatus.COMPLETED
                )
            )

    def test_callback_on_fail(self, pipeline, file):
        with patch(pipeline) as mock_pipeline:
            source_entity = SourceEntity(info=Mock(), file=file)
            source_indexer = SourceIndexer(vector_index=Mock(), openai_client=Mock(), chunk_resource_repo=Mock())

            callback = Mock()
            mock_pipeline.return_value.run.side_effect = Exception("test error")

            source_indexer.index_source(source_entity, callback)

            callback.assert_called_once_with(
                SourceInfo(
                    id=ANY,
                    type=ANY,
                    name=ANY,
                    status=IndexingStatus.FAILED
                )
            )
