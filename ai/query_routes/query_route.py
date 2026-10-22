import asyncio
import logging
from abc import ABC, abstractmethod
from typing import List, AsyncIterable, Optional

from pydantic import BaseModel

from ai.indexing.embedder.embedder import Embedder
from ai.indexing.vector_index.vector_index import VectorIndex
from ai.models.standard_llm import StandardLLM
from business.ai.ai_facade import ResponsePacket, ResponsePacketType
from business.entity.conversation.message_entity import MessageEntity
from business.entity.source.source_chunk import SourceChunk
from business.repository.medicine_info.medicine_info_repository import MedicineInfoRepository
from core.lang.supported_lang import SupportedLanguages


class QueryRoute(ABC):

    @abstractmethod
    def run(self, chat_history: List[MessageEntity], user_message: str) -> AsyncIterable[ResponsePacket]:
        pass

    def _get_sources_for_answer(self, chunks: List[SourceChunk]) -> dict[int, list[SourceChunk]]:
        sources_info = {}
        for i, chunk in enumerate(chunks):
            sources_info[i + 1] = [chunk.source_id, chunk.metadata.get("page_numbers")]
        return sources_info

    def _get_sources_packet(self, chunks: List[SourceChunk]) -> ResponsePacket:
        sources_info = self._get_sources_for_answer(chunks)
        return ResponsePacket(
            type=ResponsePacketType.SOURCES,
            content=sources_info
        )

    def _get_takeaway_sources_packet(self, chunks: List[SourceChunk]) -> ResponsePacket:
        sources_info = self._get_sources_for_answer(chunks)
        return ResponsePacket(
            type=ResponsePacketType.TAKEAWAY_SOURCES,
            content=sources_info
        )

    async def _no_info_response(self, query: str) -> AsyncIterable[ResponsePacket]:
        NO_RESPONSE_MSG = "Sayın Hocam,\nsorunuz benim eğitim aldığım konuların dışında olduğu için üzülerek cevap veremiyorum. İsterseniz destek ekibimizle iletişime geçip bu konunun eklenmesi talep edebilirsiniz. E-posta adresi: team@hekades.com"
        yield ResponsePacket(type=ResponsePacketType.TOKEN, content=NO_RESPONSE_MSG)


class ActiveSubstances(BaseModel):
    active_substance_names: list[str]
