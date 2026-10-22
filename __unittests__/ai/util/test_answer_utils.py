import pytest
from ai.utils.answer_utils import consolidate_sources
from business.entity.source.source_chunk import SourceChunk

test_case_1 = (
    {
        "tag1": [SourceChunk(source_id="1", chunk_id="", content="", summary="", metadata={"page_numbers": "1, 2, 3"})],
        "tag2": [SourceChunk(source_id="1", chunk_id="", content="", summary="", metadata={"page_numbers": "4, 5, 6"}),
                 SourceChunk(source_id="2", chunk_id="", content="", summary="", metadata={"page_numbers": "4, 5, 6"})],
    },
    {
        "tag1": "This is a [1] test",
        "tag2": "This is a [1, 2] test",
    },
    {
        "tag1": "This is a [1] test",
        "tag2": "This is a [2,3] test"
    },
    [
        SourceChunk(source_id="1", chunk_id="", content="", summary="", metadata={"page_numbers": "1, 2, 3"}),
        SourceChunk(source_id="1", chunk_id="", content="", summary="", metadata={"page_numbers": "4, 5, 6"}),
        SourceChunk(source_id="2", chunk_id="", content="", summary="", metadata={"page_numbers": "4, 5, 6"})
    ]
)

test_case_2 = (
    {
        "tag1": [
            SourceChunk(source_id=str(i), chunk_id="", content="", summary="", metadata={"page_numbers": "1, 2, 3"}) for
            i in range(1, 100)],
        "tag2": [
            SourceChunk(source_id=str(i), chunk_id="", content="", summary="", metadata={"page_numbers": "1, 2, 3"}) for
            i in range(101, 200)],
    },
    {
        "tag1": "A cit [4,9], another [29, 13]. This is a [1] test. And [205]",  # Non existent source
        "tag2": "This is a [1, 2] test. Oh [81, 99] and [13, 12]. and [1, 2, 3]",
    },
    {
        "tag1": "A cit [1,2], another [3,4]. This is a [5] test. And ",
        "tag2": "This is a [6,7] test. Oh [8,9] and [10,11]. and [6,7,12]",
    },
    [
        SourceChunk(source_id="4", chunk_id="", content="", summary="", metadata={"page_numbers": "1, 2, 3"}),
        SourceChunk(source_id="9", chunk_id="", content="", summary="", metadata={"page_numbers": "1, 2, 3"}),
        SourceChunk(source_id="29", chunk_id="", content="", summary="", metadata={"page_numbers": "1, 2, 3"}),
        SourceChunk(source_id="13", chunk_id="", content="", summary="", metadata={"page_numbers": "1, 2, 3"}),
        SourceChunk(source_id="1", chunk_id="", content="", summary="", metadata={"page_numbers": "1, 2, 3"}),
        SourceChunk(source_id="101", chunk_id="", content="", summary="", metadata={"page_numbers": "1, 2, 3"}),
        SourceChunk(source_id="102", chunk_id="", content="", summary="", metadata={"page_numbers": "1, 2, 3"}),
        SourceChunk(source_id="181", chunk_id="", content="", summary="", metadata={"page_numbers": "1, 2, 3"}),
        SourceChunk(source_id="199", chunk_id="", content="", summary="", metadata={"page_numbers": "1, 2, 3"}),
        SourceChunk(source_id="113", chunk_id="", content="", summary="", metadata={"page_numbers": "1, 2, 3"}),
        SourceChunk(source_id="112", chunk_id="", content="", summary="", metadata={"page_numbers": "1, 2, 3"}),
        SourceChunk(source_id="103", chunk_id="", content="", summary="", metadata={"page_numbers": "1, 2, 3"}),
    ]
)


@pytest.mark.parametrize("dummy_sources, dummy_answers, answers, sources", [
    test_case_1,
    test_case_2
])
def test_consolidate_sources(dummy_sources, dummy_answers, answers, sources):
    print(dummy_sources)
    consolidated_sources = consolidate_sources(dummy_sources, dummy_answers)
    assert dummy_answers == answers
    assert consolidated_sources == sources
