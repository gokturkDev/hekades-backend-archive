import json
import logging
from typing import List, AsyncIterable, Optional

from pydantic import BaseModel

from ai.indexing.embedder.embedder import Embedder
from ai.indexing.vector_index.vector_index import VectorIndex
from ai.models.standard_llm import StandardLLM
from ai.query_routes.information.prompts import INFORMATION_QUERY_EXPANSION_PROMPT, KNOWLEDGE_BANK_PROMPT, \
    KNOWLEDGE_BANK_PROMPT_WITH_RECORD, RECORD_TO_GUIDELINE, TAG_SELECTION_MESSAGE_PROMPT, \
    TAG_SELECTION_WITH_RECORD_PROMPT, QUERY_REFORMULATION_PROMPT, QUERY_REFORMULATION_EXTRACTION_PROMPT, \
    PATIENT_QUERY_REFORMULATION_EXTRACTION_PROMPT, PATIENT_QUERY_REFORMULATION_PROMPT
from ai.query_routes.information.prompts import TAG_SELECTION_PROMPT
from ai.query_routes.query_route import QueryRoute
from ai.retrieval.fusion.doc_aware_multilang_fusion_retriever import DocAwareMultilangFusionRetriever
from ai.retrieval.tag.tag_selector import TagSelector
from business.ai.ai_facade import ResponsePacket, ResponsePacketType
from business.entity.conversation.message_entity import MessageEntity
from business.entity.source.source_chunk import SourceChunk
from business.repository.medicine_info.medicine_info_repository import MedicineInfoRepository
from core.lang.supported_lang import SupportedLanguages


def hydrate_prompt(context_docs: List[SourceChunk], language, patient_record: Optional[str] = None) -> str:
    if patient_record:
        return KNOWLEDGE_BANK_PROMPT_WITH_RECORD.format(
            context_docs_str="\n".join(
                [f"Source {i + 1}\n---------------------\n{doc.content}\n---------------------" for i, doc in
                 enumerate(context_docs)]),
            language=language.value,
            patient_record=patient_record
        )
    return KNOWLEDGE_BANK_PROMPT.format(
        context_docs_str="\n".join(
            [f"Source {i + 1}\n---------------------\n{doc.content}\n---------------------" for i, doc in
             enumerate(context_docs)]),
        language=language.value
    )


logger = logging.getLogger("hekades")


class InformationQueryRoute(QueryRoute):
    def __init__(self, vector_index: VectorIndex, medicine_info_repo: MedicineInfoRepository,
                 expensive_model: StandardLLM,
                 moderate_model: StandardLLM, cheap_model: StandardLLM,
                 logger: logging.Logger, language: SupportedLanguages, embedder: Optional[Embedder] = None,
                 patient_record: Optional[str] = None):
        self.patient_record = patient_record
        self.moderate_model = moderate_model
        self.expensive_model = expensive_model
        self.cheap_model = cheap_model
        self.vector_index = vector_index
        self.language = language
        self.embedder = embedder
        self.medicine_info_repo = medicine_info_repo
        self.logger = logger
        if self.patient_record:
            tag_selection_prompt = TAG_SELECTION_WITH_RECORD_PROMPT
        else:
            tag_selection_prompt = TAG_SELECTION_PROMPT

        self.tag_selector = TagSelector(logger, self.moderate_model, self.cheap_model,
                                        tag_selection_prompt=tag_selection_prompt)
        self.retriever = DocAwareMultilangFusionRetriever(ai_model=self.cheap_model, vector_index=self.vector_index,
                                                          query_expansion_prompt=INFORMATION_QUERY_EXPANSION_PROMPT,
                                                          logger=self.logger,
                                                          embedder=self.embedder, alpha=0.75)

    async def run(self, chat_history: List[MessageEntity], user_message: str) -> AsyncIterable[ResponsePacket]:
        user_message = await self._reformulate_query(user_message=user_message)
        message = await self._transform_user_message_for_tags(user_message)

        yield ResponsePacket(type=ResponsePacketType.STAGE_COMPLETED)

        tags = await self.tag_selector.get_tags(message)

        yield ResponsePacket(type=ResponsePacketType.STAGE_COMPLETED)

        chunks = await self.retriever.retrieve(user_message, tags)

        if len(chunks) == 0:
            self.logger.info(f"No chunks were found for query {user_message}, responding with no_info response ")
            async for packet in self._no_info_response(user_message):
                yield packet
            return

        self.logger.info("\n".join([f"Reference Source {i + 1}:\n{chunk.content}" for i, chunk in enumerate(chunks)]))
        yield self._get_sources_packet(chunks)

        prompt = hydrate_prompt(chunks, self.language, self.patient_record)
        self.logger.info(f"Here's the prompt:\n{prompt}")
        generated_answer = ""
        async for token in self.expensive_model.get_token_stream(user_msg=user_message, prompt=prompt):
            if token is not None:
                yield ResponsePacket(type=ResponsePacketType.TOKEN, content=token)
                generated_answer += token

        self.logger.info("Information Query route completed")

    async def _transform_user_message_for_tags(self, user_message):
        if self.patient_record:
            record_to_guideline = await self.expensive_model.get_response(prompt=RECORD_TO_GUIDELINE,
                                                                          user_msg=user_message)
            self.logger.info(f"Here's the record to guideline:\n{record_to_guideline}")
            message = TAG_SELECTION_MESSAGE_PROMPT.format(
                patient_record=self.patient_record,
                record_to_guideline=record_to_guideline,
                user_message=user_message
            )
        else:
            message = user_message
        return message

    async def _reformulate_query(self, user_message: str) -> str:
        class ResponseModel(BaseModel):
            final_question: str

        if self.patient_record:
            model = await self._get_reformulated_query(ResponseModel,
                                                       extraction_prompt=PATIENT_QUERY_REFORMULATION_EXTRACTION_PROMPT,
                                                       reformulation_prompt=PATIENT_QUERY_REFORMULATION_PROMPT.format(
                                                           patient_record=self.patient_record
                                                       ),
                                                       user_message=user_message)
        else:
            model = await self._get_reformulated_query(ResponseModel,
                                                       extraction_prompt=QUERY_REFORMULATION_EXTRACTION_PROMPT,
                                                       reformulation_prompt=QUERY_REFORMULATION_PROMPT,
                                                       user_message=user_message)
        return model.final_question

    async def _get_reformulated_query(self, ResponseModel, extraction_prompt, reformulation_prompt, user_message):
        res = await self.expensive_model.get_response(prompt=reformulation_prompt, user_msg=user_message)
        self.logger.info(f"Here's reformulation reasoning:\n{res}")
        model = await self.expensive_model.get_response_with_response_model(prompt=extraction_prompt,
                                                                            user_msg=res,
                                                                            response_model=ResponseModel)
        return model
