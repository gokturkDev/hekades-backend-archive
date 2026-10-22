from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ChunkType(Enum):
    CONTENT = "content"
    TABLE_OF_CONTENTS = "TOC"


class SourceChunk(BaseModel):
    source_id: str
    chunk_id: str
    content: str
    summary: str
    metadata: dict
    content_embedding: Optional[list[float]] = None
    summary_embedding: Optional[list[float]] = None
    score: Optional[float] = None
    chunk_type: ChunkType = ChunkType.CONTENT
    tags: Optional[list[str]] = None
