import logging
from business.entity.source.source_chunk import SourceChunk

logger = logging.getLogger("hekades")


def get_source_to_page_num_mapping(chunks: list[SourceChunk]):
    source_info = {}
    for chunk in chunks:
        if chunk.metadata is not None and chunk.metadata.get("page_numbers") is not None:
            if chunk.source_id not in source_info:
                source_info[chunk.source_id] = []

            page_rank_tuple = (chunk.metadata.get("page_numbers"), chunk.score)
            source_info[chunk.source_id].append(page_rank_tuple)

    return source_info
