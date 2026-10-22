from uuid import uuid4

from ai.query_routes.utils.chunk_utils import consolidate_chunk_citations
from business.entity.source.source_chunk import SourceChunk


def test_consolidate_chunk_citations():
    citations, chunks = consolidate_chunk_citations(test_chunks)
    assert citations == expected_citations


test_chunks = [
    SourceChunk(
        content="This is a test {/1/} citation",
        metadata={"citations": [{"citation_id": "1", "name": "cit A"}]},
        chunk_id=str(uuid4()),
        source_id=str(uuid4())
    ),
    SourceChunk(
        content="This is a test {/1/} citation",
        metadata={"citations": [{"citation_id": "1", "name": "cit B"}]},
        chunk_id=str(uuid4()),
        source_id=str(uuid4())
    ),
    SourceChunk(
        content="This is a test {/2/} citation",
        metadata={"citations": [{"citation_id": "2", "name": "cit A"}]},
        chunk_id=str(uuid4()),
        source_id=str(uuid4())
    ),
    SourceChunk(
        content="This is a test {/1,2/} citation",
        metadata={"citations": [
            {"citation_id": "1", "name": "cit C"},
            {"citation_id": "2", "name": "cit D"}
        ]},
        chunk_id=str(uuid4()),
        source_id=str(uuid4())
    ),
    SourceChunk(
        content="This is a test {/1,2/} citation",
        metadata={"citations": [
            {"citation_id": "1", "name": "cit D"},
            {"citation_id": "2", "name": "cit E"}
        ]},
        chunk_id=str(uuid4()),
        source_id=str(uuid4())
    ),
    SourceChunk(
        content="This is a test {/3,4/} citation",
        metadata={"citations": [
            {"citation_id": "3", "name": "cit F"},
            {"citation_id": "4", "name": "cit E"}
        ]},
        chunk_id=str(uuid4()),
        source_id=str(uuid4())
    ),
    SourceChunk(
        content="This is a test without citation",
        metadata={"citations": []},
        chunk_id=str(uuid4()),
        source_id=str(uuid4())
    ),
]

expected_citations = {
    "1": {
        "name": "cit A"
    },
    "2": {
        "name": "cit B"
    },
    "3": {
        "name": "cit C"
    },
    "4": {
        "name": "cit D"
    },
    "5": {
        "name": "cit E"
    },
    "6": {
        "name": "cit F"
    }
}
