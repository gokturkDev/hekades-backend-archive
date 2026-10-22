from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ConversationType(str, Enum):
    information = "information"
    case = "case"


class ConversationEntity(BaseModel):
    convo_id: str
    title: str
    user_email: str
    created_at: datetime
    patient_id: Optional[str] = None
    literature_docs: Optional[list[dict]] = None
    pubmed_summary: Optional[str] = None
    confidence_index: Optional[int] = None
    type: Optional[ConversationType] = None
