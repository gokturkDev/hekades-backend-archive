from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Union, AsyncIterable, Optional

from pydantic import BaseModel

from business.entity.conversation.message_entity import MessageEntity
from business.entity.patient.patient_entity import PatientEntity
from core.lang.supported_lang import SupportedLanguages


class ResponsePacketType(str, Enum):
    QUESTION_TYPE = "question_type"
    CONVERSATION_INFO = "conversation_info"
    SOURCES = "sources"
    TAKEAWAY_SOURCES = "takeaway_sources"
    LITERATURE_DOCUMENTS = "literature_docs"
    LITERATURE_SUMMARY_TOKEN = "literature_summary_token"
    CONFIDENCE_INDEX = "confidence_index"
    MEDICINE_INFO = "medicine_info"
    TOKEN = "token"
    TAKEAWAY_TOKEN = "takeaway_token"
    STAGES = "stages"
    STAGE_COMPLETED = "stage_completed"


class ResponsePacket(BaseModel):
    type: ResponsePacketType
    content: Optional[Union[str, list, dict, int]] = None


class AIFacade(ABC):

    @abstractmethod
    def respond_to_user(self, chat_history: List[MessageEntity], convo_id: str, user_message: str,
                        language: SupportedLanguages, patient: Optional[PatientEntity] = None) -> \
            AsyncIterable[ResponsePacket]:
        pass

    @abstractmethod
    def pubmed_search(self, convo_id: str, user_message: str, language: SupportedLanguages, patient: Optional[PatientEntity] = None) -> AsyncIterable[
        ResponsePacket]:
        pass

    @abstractmethod
    async def summarize_patient_record(self, patient: PatientEntity) -> str:
        pass
