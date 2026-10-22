from enum import Enum
from typing import Optional

from pydantic import BaseModel


class IndexingStatus(Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class SourceType(Enum):
    INDEX = "INDEX"
    DISPLAY = "DISPLAY"


class SourceInfo(BaseModel):
    id: str
    name: str
    status: IndexingStatus
    type: Optional[SourceType] = None
    link: Optional[str] = None
