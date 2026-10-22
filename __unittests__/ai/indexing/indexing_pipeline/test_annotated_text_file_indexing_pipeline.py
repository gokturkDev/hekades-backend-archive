import io
from unittest.mock import Mock

import pytest

from ai.indexing.indexing_pipeline.annotated_text_file_indexing_pipeline import AnnotatedTextFileIndexingPipeline
from ai.indexing.vector_index.vector_index import VectorIndex
from ai.models.standard_llm import StandardLLM
from business.entity.source.source_chunk import SourceChunk, ChunkType
from business.entity.source.source_entity import SourceEntity
from business.entity.source.source_info import SourceInfo, IndexingStatus
from core.utils.file import File

text = """
{!TAG!}
Some tag
Some other tag
{!ENDTAG!}

{!TOC!}
This is the toc of the document
{!ENDTOC!}

{&22&}

✅ Diyabetli bireylerde en sık görülen kardiyovasküler hastalıklar; koroner arter hastalığı, periferik arter hastalığı, inme ve sistolik, diyastolik kalp yetersizliğidir. ✅.
✅ 
Kardiyovasküler mortalite nedeni olarak öncelikle koroner arter hastalığı düşünülse de olguların önemli bir kısmında kalp yetersizliği gibi iskemik olmayan hastalıklar ölüme neden olmaktadırlar.
✅. 
{&23&}
✅Bu nedenle, diyabetli bireylerde yapısal ve işlevsel kardiyak sorunlar açısından tarama yapılması ve erken tanı ve önleyici tedavi stratejileri çok önemlidir.
{&24&}
Diyabetik kardiyomiyopati tanımı ve diyabetin tek başına kardiyomiyopatiye neden olup olmadığı uzun süredir tartışılmaktadır. Diyabetik kardiyomiyopatinin koroner arter hastalığı ve eşlik eden HT gibi nedenlere bağlı gelişebileceği savunulsa da günümüzde, diyabetik kardiyomiyopatinin gerçek bir hastalık olduğu genel olarak kabul edilmektedir.
✅.
✅ 
Diyabete bağlı kardiyomiyopatinin gelişmesinde sol ventrikül hipertrofisi, diyastolik disfonksiyon, azalmış kardiyak fonksiyonel rezerv ile sonuçlanan insülin direnci, metabolik bozukluklar ve otonom disfonksiyonu gibi birçok mekanizma rol oynamaktadır. Son veriler, diyabet ve kalp kapak hastalığı arasında da ilişki olabileceğini, hafif derecede kapak hastalığının olumsuz prognoz göstergesi olabileceğini göstermektedir.✅.

"""
expected_chunks = [
    SourceChunk(
        chunk_id="123",
        source_id="123",
        content="This is the toc of the document",
        summary="summary",
        chunk_type=ChunkType.TABLE_OF_CONTENTS,
        tags=["Some tag", "Some other tag"],
        metadata={
            "page_numbers": [1]
        }
    ),
    SourceChunk(
        chunk_id="123",
        source_id="123",
        content="Diyabetli bireylerde en sık görülen kardiyovasküler hastalıklar; koroner arter hastalığı, periferik arter hastalığı, inme ve sistolik, diyastolik kalp yetersizliğidir.",
        summary="summary",
        tags=["Some tag", "Some other tag"],
        metadata={
            "page_numbers": [1, 22]
        }
    ),
    SourceChunk(
        chunk_id="123",
        source_id="123",
        content="Kardiyovasküler mortalite nedeni olarak öncelikle koroner arter hastalığı düşünülse de olguların önemli bir kısmında kalp yetersizliği gibi iskemik olmayan hastalıklar ölüme neden olmaktadırlar.",
        summary="summary",
        tags=["Some tag", "Some other tag"],
        metadata={
            "page_numbers": [22]
        }
    ),
    SourceChunk(
        chunk_id="123",
        source_id="123",
        content="Bu nedenle, diyabetli bireylerde yapısal ve işlevsel kardiyak sorunlar açısından tarama yapılması ve erken tanı ve önleyici tedavi stratejileri çok önemlidir.\n\nDiyabetik kardiyomiyopati tanımı ve diyabetin tek başına kardiyomiyopatiye neden olup olmadığı uzun süredir tartışılmaktadır. Diyabetik kardiyomiyopatinin koroner arter hastalığı ve eşlik eden HT gibi nedenlere bağlı gelişebileceği savunulsa da günümüzde, diyabetik kardiyomiyopatinin gerçek bir hastalık olduğu genel olarak kabul edilmektedir.",
        summary="summary",
        tags=["Some tag", "Some other tag"],
        metadata={
            "page_numbers": [24, 23]
        }
    ),
    SourceChunk(
        chunk_id="123",
        source_id="123",
        content="Diyabete bağlı kardiyomiyopatinin gelişmesinde sol ventrikül hipertrofisi, diyastolik disfonksiyon, azalmış kardiyak fonksiyonel rezerv ile sonuçlanan insülin direnci, metabolik bozukluklar ve otonom disfonksiyonu gibi birçok mekanizma rol oynamaktadır. Son veriler, diyabet ve kalp kapak hastalığı arasında da ilişki olabileceğini, hafif derecede kapak hastalığının olumsuz prognoz göstergesi olabileceğini göstermektedir.",
        summary="summary",
        tags=["Some tag", "Some other tag"],
        metadata={
            "page_numbers": [24]
        }
    )
]


@pytest.fixture()
def mock_vector_index():
    return Mock(spec=VectorIndex)


@pytest.fixture()
def mock_ai_model():
    mock = Mock(spec=StandardLLM)
    mock.get_response.return_value = "Summary"
    return mock


def test_annotated_text_file_indexing_pipeline(mock_vector_index, mock_ai_model):
    source = SourceEntity(
        file=File(file_io=io.BytesIO(text.encode("utf-8")), filename="filename"),
        info=SourceInfo(
            id="123",
            status=IndexingStatus.IN_PROGRESS,
            name="name"

        )
    )
    pipeline = AnnotatedTextFileIndexingPipeline(mock_vector_index, mock_ai_model)
    pipeline.run(source)
    chunks = mock_vector_index.index_chunks.call_args[0][0]
    for i, chunk in enumerate(chunks):
        expected_chunk = expected_chunks[i]
        assert chunk.content == expected_chunk.content
        assert chunk.metadata == expected_chunk.metadata
        assert chunk.tags == expected_chunk.tags
        assert chunk.chunk_type == expected_chunk.chunk_type
        assert len(chunk.summary) > 0
