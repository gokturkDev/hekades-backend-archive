from enum import Enum
from typing import Union, Optional

from pydantic import BaseModel

from core.lang.supported_lang import SupportedLanguages


class WebsocketConversationData(BaseModel):
    message: str
    language: SupportedLanguages
    patient_id: Optional[str] = None

class WebsocketConversationPubmed(BaseModel):
    language: SupportedLanguages
    conversation_id: str

class WebsocketUserPacketType(str, Enum):
    NEW_CONVO = "new_conversation"
    PUBMED_REQUEST = "pubmed_request"


class WebsocketUserPacket(BaseModel):
    type: WebsocketUserPacketType
    content: Union[WebsocketConversationData, WebsocketConversationPubmed]
