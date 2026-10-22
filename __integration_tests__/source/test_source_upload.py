from os.path import dirname, join

import inject
import pytest

from __test_utils__.chunking import text_word_equivalence
from __test_utils__.get_test_client import get_test_client_with_dependencies
from __test_utils__.test_file_factory import TestFileFactory
from business.entity.source.source_info import IndexingStatus
from main.dependency_container import DepContainer


@pytest.fixture(scope="session")
def api_client():
    client = get_test_client_with_dependencies()
    return client


def valid_sources():
    return [
        {
            "source_name": "test source",
            "index_file": TestFileFactory.create_test_file_from_path(
                join(dirname(__file__), "simple_annotated_file.txt")
            ),
            "display_file": TestFileFactory.create_test_file_from_path(
                join(dirname(__file__), "simple_annotated_file.txt")
            ),
            "file_type": "txt"  # This is for testing purposes only
        },
        {
            "source_name": "test source 2",
            "index_file": TestFileFactory.create_test_file_from_path(
                join(dirname(__file__), "page_annotated_file.txt")
            ),
            "display_file": TestFileFactory.create_test_file_from_path(
                join(dirname(__file__), "sample_guideline.pdf")
            ),
            "file_type": "txt"  # This is for testing purposes only
        }

        # DON'T TEST PDF AS ITS TEMPORARILY DISABLED
        # {
        #    "source_name": "sample guideline",
        #    "source_file": TestFileFactory.create_test_file_from_path(
        #        join(dirname(__file__), "sample_guideline.pdf")
        #    ),
        #    "source_file_type": "pdf"
        # }

    ]


@pytest.fixture(scope="class", params=valid_sources())
def setup_class(api_client, request):
    source = request.param
    source_name = source["source_name"]
    source_id = upload_source(api_client, source_name, source["index_file"], source["display_file"])
    source["source_id"] = source_id
    request.cls.source = source
    yield
    api_client.delete(f"/source/{source_id}")


def upload_source(api_client, source_name, index_file, display_file):
    response = api_client.post(
        "/source/",
        data={
            "source_name": source_name
        },
        files={
            "index_file": (index_file.filename, index_file.file_io),
            "display_file": (display_file.filename, display_file.file_io)
        }
    )
    assert response.status_code == 200
    source_id = response.json()["source_id"]
    assert source_id is not None
    return source_id


@pytest.mark.usefixtures("setup_class")
class TestSourceUpload:
    @classmethod
    def setup_class(cls):
        cls.source_repo = inject.instance(DepContainer).source_repo
        cls.vector_index = inject.instance(DepContainer).vector_index

    def test_uploaded_source_info_present(self):
        source_id = self.source["source_id"]
        source_infos = self.source_repo.get_all_sources_info()

        for info in source_infos:
            if info.id == source_id:
                assert info.status == IndexingStatus.COMPLETED.value
                return
        raise AssertionError("Source isn't present in infos")

    def test_display_file_same(self):
        source_id = self.source["source_id"]

        source_file = self.source_repo.get_source_display_file_from_id(source_id)
        test_file = self.source["display_file"]

        source_file.file_io.seek(0)
        test_file.file_io.seek(0)
        assert source_file.file_io.read() == test_file.file_io.read()
        assert source_file.filename == test_file.filename

    def test_uploaded_source_vector_index(self):
        source_id = self.source["source_id"]
        source_chunks = self.vector_index.get_chunks_of_source(source_id)
        assert len(source_chunks) > 0

        text = ""
        for chunk in source_chunks:
            assert chunk.source_id == source_id
            assert chunk.content_embedding is not None
            text += chunk.content
            if 'has_resource' in chunk.metadata:
                assert chunk.metadata['has_resource'] is True

        if self.source["file_type"] == "txt":
            test_file = self.source["index_file"]
            test_file.file_io.seek(0)
            document_text = test_file.file_io.read().decode("utf-8")
            # Settle for approximate equivalence as the text might be tokenized differently
            # and overlaps might not be perfect
            assert text_word_equivalence(document_text, text) >= 0.95


def invalid_sources():
    return [
        {
            "source_name": "test",
            "index_file": TestFileFactory.create_test_file_from_string(
                "test.txt", b""
            ),
            "display_file": TestFileFactory.create_test_file_from_string(
                "test.txt", b""
            )
        },
        {
            "source_name": "test",
            "index_file": TestFileFactory.create_test_file_from_string(
                "test.pdf", b""
            ),
            "display_file": TestFileFactory.create_test_file_from_string(
                "test.pdf", b""
            )
        },
        {
            "source_name": "test",
            "index_file": TestFileFactory.create_test_file_from_string(
                "test", b"test content"
            ),
            "display_file": TestFileFactory.create_test_file_from_string(
                "test", b"test content"
            )
        }
    ]


@pytest.mark.parametrize("source", invalid_sources())
def test_rejects_invalid(api_client, source):
    source_name = source["source_name"]
    response = api_client.post(
        "/source/",
        data={
            "source_name": source_name
        },
        files={
            "index_file": (source["index_file"].filename, source["index_file"].file_io),
            "display_file": (source["display_file"].filename, source["display_file"].file_io)
        }
    )
    assert response.status_code == 400
