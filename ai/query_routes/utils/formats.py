from business.entity.source.source_chunk import SourceChunk


def format_source_chunks(chunks: list[SourceChunk]):
    return "\n".join(
    [f"Source {i + 1}:\n------------------------------\n{doc.content}\n------------------------------\n" for
        i, doc in enumerate(chunks)])