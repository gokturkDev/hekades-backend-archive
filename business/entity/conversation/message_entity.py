from abc import ABC
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MessageEntity(ABC, BaseModel):
    role: str
    convo_id: str
    order: int
    created_at: datetime


class UserMessageEntity(MessageEntity):
    role: str = "user"
    content: str


class SystemMessageEntity(MessageEntity):
    role: str = "ai"
    phases: dict = {}
    sources: dict = {}
    content: Optional[str] = None  # For backward compatibility
