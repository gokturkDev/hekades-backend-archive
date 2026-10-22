import asyncio
import logging
from typing import List, AsyncIterator, Optional, Type, AsyncGenerator

from pydantic import BaseModel, Field

from ai.indexing.embedder.embedder import Embedder
from ai.indexing.vector_index.vector_index import VectorIndex
from ai.models.aws_models.cohere_command_r_model import CohereCommandRModel
from ai.models.standard_llm import StandardLLM
from ai.query_routes.case.prompts import FINAL_TAG_SELECTION_PROMPT, INTEGRATION_PROMPT, INITIAL_ASSESSMENT_PROMPT, \
    Q_SCOPE_PROMPT, QUERY_EXPANSION_PROMPT, QUERY_REFORMULATION_EXTRACTION_PROMPT, QUERY_REFORMULATION_PROMPT, \
    RICH_QUERY_PROMPT, TAG_REFORMULATION_PROMPT, TAG_SELECTION_PROMPT, TAKEAWAY_PROMPT
from ai.query_routes.case.response_models import AssessmentForm
from ai.query_routes.query_route import QueryRoute
from ai.query_routes.tag_agent.tag_agent_answer import TagAgentAnswer
from ai.query_routes.utils.formats import format_source_chunks
from ai.retrieval.tag.tag_selector import TagSelector, TagSelectorResponseModel
from ai.utils.answer_utils import consolidate_sources
from business.ai.ai_facade import ResponsePacket, ResponsePacketType
from business.entity.conversation.message_entity import MessageEntity
from business.entity.source.source_chunk import SourceChunk
from business.repository.medicine_info.medicine_info_repository import MedicineInfoRepository
from core.lang.supported_lang import SupportedLanguages


class SearchQueries(BaseModel):
    queries: list[str]


class Topics(BaseModel):
    topic_list: list[str]


class Queries(BaseModel):
    query_list: list[str]


QUERY_EXTRACTION_PROMPT = """
You are given a reasoning about formulating new queries for a question.
Your task is to extract the final queries as is and put them in the query_list.
ONLY EXTRACT THE FINAL QUERIES AS IS! THIS IS EXTREMELY IMPORTANT!
"""


def hydrate_prompt(prompt: str, question: Optional[str] = None,
                   current_answer: Optional[str] = None, context: Optional[list[SourceChunk]] = None,
                   outline_headings: list[str] = None, disease_to_disease: Optional[str] = None,
                   complaints_to_disease: Optional[str] = None, patient_record: Optional[str] = None) -> str:
    my_format_map = {
    }
    if question is not None:
        my_format_map["question"] = question
    if current_answer is not None:
        my_format_map["current_answer"] = current_answer
    if context is not None:
        my_format_map["context"] = format_source_chunks(context)
    if outline_headings is not None:
        my_format_map["outline_headings"] = "\n".join([f"-{heading}" for heading in outline_headings])
    if disease_to_disease is not None:
        my_format_map["disease_to_disease"] = disease_to_disease
    if complaints_to_disease is not None:
        my_format_map["complaints_to_disease"] = complaints_to_disease
    if patient_record is not None:
        my_format_map["patient_record"] = patient_record

    return prompt.format_map(my_format_map)


class CaseQueryRoute(QueryRoute):

    def __init__(self, vector_index: VectorIndex, medicine_info_repo: MedicineInfoRepository,
                 expensive_model: StandardLLM,
                 expensive_instruct_model: StandardLLM,
                 rag_model: CohereCommandRModel,
                 moderate_model: StandardLLM, cheap_model: StandardLLM,
                 logger: logging.Logger, language: SupportedLanguages, embedder: Optional[Embedder] = None,
                 patient_record: Optional[str] = None):

        self.vector_index = vector_index
        self.medicine_info_repo = medicine_info_repo
        self.expensive_model = expensive_model
        self.expensive_instruct_model = expensive_instruct_model
        self.rag_model = rag_model
        self.moderate_model = moderate_model
        self.cheap_model = cheap_model
        self.logger = logger
        self.embedder = embedder
        self.language = language
        self.patient_record = patient_record

        self.tag_selector = TagSelector(logger, self.moderate_model, self.cheap_model,
                                        tag_selection_prompt=TAG_SELECTION_PROMPT)

    async def run(self, chat_history: List[MessageEntity], user_message: str) -> AsyncIterator[ResponsePacket]:
        if self.patient_record:
            tag_message, new_user_message = None, None
            async with asyncio.TaskGroup() as tg:
                async def user_msg_reformulation():
                    nonlocal new_user_message
                    new_user_message = await self._reformulate_query_for_patient(user_message,
                                                                                 QUERY_REFORMULATION_PROMPT)
                    self.logger.info(f"New user message:\n{new_user_message}")

                async def tag_msg_reformulation():
                    nonlocal tag_message
                    tag_message = await self._reformulate_query_for_patient(user_message, TAG_REFORMULATION_PROMPT)
                    self.logger.info(f"Tag message:\n{tag_message}")

                tg.create_task(user_msg_reformulation())
                tg.create_task(tag_msg_reformulation())

            user_message = new_user_message

        await self.initialize_prompts()

        if not self.patient_record:
            init_prompt = hydrate_prompt(INITIAL_ASSESSMENT_PROMPT, user_message)

            form_stream = await self.expensive_model.get_streaming_response_with_response_model(user_msg=user_message,
                                                                                                prompt=init_prompt,
                                                                                                response_model=AssessmentForm)
            fields_to_headers = AssessmentForm.get_headers_for_fields()

            generated_answer = ""
            async for packet in self._process_partial_form(form_stream, AssessmentForm,
                                                           ResponsePacketType.TOKEN, fields_to_headers):
                if packet.content is not None:
                    generated_answer += packet.content
            self.patient_record = generated_answer
            tag_message = user_message

        yield ResponsePacket(type=ResponsePacketType.STAGE_COMPLETED)

        rich_query = hydrate_prompt(
            RICH_QUERY_PROMPT,
            user_message,
            patient_record=self.patient_record,
        )

        all_tags = set()

        lock = asyncio.Lock()

        async with asyncio.TaskGroup() as tg:
            async def get_tags(ai_model):
                nonlocal all_tags
                tag_selector = TagSelector(self.logger, ai_model, self.cheap_model,
                                           tag_selection_prompt=TAG_SELECTION_PROMPT)
                tags = await tag_selector.get_tags(tag_message)
                async with lock:
                    all_tags.update(tags)

            tg.create_task(get_tags(self.moderate_model))
            tg.create_task(get_tags(self.expensive_instruct_model))

        self.logger.info(f"All Tags: {all_tags}")
        final_tag_selector = self._setup_final_tag_selector(user_message)
        tags = await final_tag_selector.get_tags(tag_message, tags=all_tags, use_descriptions=True)
        self.logger.info(f"Final Tags: {tags}")
        yield ResponsePacket(type=ResponsePacketType.STAGE_COMPLETED)

        generated_answer = ""
        async for packet in self._answer_generator(tags, user_message, rich_query):
            if packet.type == ResponsePacketType.TOKEN:
                generated_answer += packet.content
            else:
                yield packet

        generated_answer = generated_answer.replace("#", "")
        integrated_prompt = INTEGRATION_PROMPT.format(
            answers=generated_answer,
            language=self.language.value
        )
        self.logger.info(f"Integration Prompt:\n{integrated_prompt}")
        
        integrated_answer = ""
        async for token in self.expensive_model.get_token_stream(prompt=integrated_prompt):
            integrated_answer += token
            yield ResponsePacket(type=ResponsePacketType.TOKEN, content=token)
        self.logger.info(f"Integration Answer:\n{integrated_answer}")

        async for token in self.expensive_model.get_token_stream(
                prompt=TAKEAWAY_PROMPT.format(
                    patient_record=self.patient_record,
                    question=user_message,
                    answers=generated_answer,
                    language=self.language.value
                )
        ):
            if token:
                yield ResponsePacket(type=ResponsePacketType.TAKEAWAY_TOKEN, content=token)

        # yield await self._get_confidence_index(user_message)
        self.logger.info("Case query route finished")

    async def _reformulate_query_for_patient(self, user_message, prompt):
        res = await self.expensive_model.get_response(
            prompt=prompt.format(
                patient_record=self.patient_record
            ),
            user_msg=user_message
        )

        class ResponseModel(BaseModel):
            reformulated_query: str

        rsp = await self.expensive_model.get_response_with_response_model(res, QUERY_REFORMULATION_EXTRACTION_PROMPT,
                                                                          ResponseModel)
        user_message = rsp.reformulated_query
        return user_message

    async def _answer_generator(self, tags, user_message, rich_query) -> AsyncGenerator[ResponsePacket, None]:
        query_reasoning = await self.cheap_model.get_response(rich_query, QUERY_EXPANSION_PROMPT)
        queries = await self.cheap_model.get_response_with_response_model(query_reasoning, QUERY_EXTRACTION_PROMPT,
                                                                          Queries)
        queries = [query for query in queries.query_list if len(query.replace(" ", "")) > 0]
        queries.append(rich_query)
        yield ResponsePacket(type=ResponsePacketType.STAGE_COMPLETED)

        answers = {}
        sources = {}

        async with asyncio.TaskGroup() as tg:
            stage_completed = {}
            tasks = []

            for tag in tags:
                task = tg.create_task(
                    self._tag_agent_answer(tag, user_message=user_message, rich_query=rich_query, answers=answers,
                                           sources=sources, queries=queries, stage_completed=stage_completed))
                tasks.append(task)

            while any(not task.done() for task in tasks):
                if len(stage_completed.values()) == len(tags):
                    yield ResponsePacket(type=ResponsePacketType.STAGE_COMPLETED)
                    stage_completed = {}

                await asyncio.sleep(0.02)

        if len(answers.items()) == 0:
            yield ResponsePacket(type=ResponsePacketType.TOKEN, content=await self._admit_ignorance())
            return

        new_sources = consolidate_sources(sources, answers)
        yield self._get_sources_packet(new_sources)
        yield self._get_takeaway_sources_packet(new_sources)

        final_answer = "\n".join(
            [f"## {TagSelector.localize_tag(tag, self.language)}\n{answer}" for tag, answer in answers.items()])
        yield ResponsePacket(type=ResponsePacketType.TOKEN, content=final_answer)

        self.logger.info(f"Answer completed!\n{final_answer}")

    async def initialize_prompts(self):
        self.integration_prompt = INTEGRATION_PROMPT

    async def _hydrate_integration(self, answers):
        return self.integration_prompt.format(answers="\n".join(
            [f"{tag} Answer {i + 1}\n-----------------------\n{content}\n-----------------------" for
             i, (tag, content) in enumerate(answers.items())]
        ), language=self.language.value)

    async def _get_confidence_index(self, query: str, retry: int = 0) -> ResponsePacket:
        class ResponseModel(BaseModel):
            total_score: int

        def convert_scale(value, old_min=3, old_max=12, new_min=45, new_max=90):
            # Ensure the input value is within the old range
            value = max(min(value, old_max), old_min)

            scale_ratio = (new_max - new_min) / (old_max - old_min)
            new_value = new_min + (value - old_min) * scale_ratio

            return new_value

        model = await self.cheap_model.get_response_with_response_model(user_msg=query, prompt=Q_SCOPE_PROMPT,
                                                                        response_model=ResponseModel)
        reverse_score = 12 - (model.total_score - 3)
        percentage_score = int(convert_scale(reverse_score))

        return ResponsePacket(
            type=ResponsePacketType.CONFIDENCE_INDEX,
            content=percentage_score
        )

    async def _process_partial_form(self, form_stream, response_model: Type[BaseModel],
                                    response_packet_type: ResponsePacketType,
                                    fieldname_to_header: dict[str, str]) -> AsyncIterator[ResponsePacket]:

        schema = response_model.model_json_schema()

        fields_looking_for = list(schema["properties"].keys())

        async for form in form_stream:

            form_dict = form.model_dump()

            for field in fields_looking_for:
                field_value = form_dict.get(field)

                if field_value:
                    fields_looking_for.remove(field)
                    header = fieldname_to_header.get(field)

                    yield ResponsePacket(
                        type=response_packet_type,
                        content=f"## {header}\n{field_value}\n"
                    )

    async def _tag_agent_answer(self, tag: str, user_message: str, rich_query: str, answers: dict[str, str],
                                sources: dict[str, list[SourceChunk]], queries: list[str], stage_completed: dict):

        agent = TagAgentAnswer(tag, self.expensive_model, self.cheap_model, self.vector_index,
                               self.logger,
                               self.embedder, self.patient_record, self.language)

        tag_answer = ""
        stage_count = 0
        async for packet in agent.execute(user_message, rich_query, queries):
            if packet.type == ResponsePacketType.SOURCES:
                sources[tag] = packet.content
            elif packet.type == ResponsePacketType.TOKEN:
                tag_answer += packet.content
                if tag_answer:
                    answers[tag] = tag_answer
            elif packet.type == ResponsePacketType.STAGE_COMPLETED:
                stage_completed[f"{str(stage_count)}{tag}"] = "completed"
                stage_count += 1

    async def _admit_ignorance(self):
        return await self.cheap_model.get_response(
            prompt=f"Translate the below text to {self.language}\n\nI'm sorry, I don't have enough information to answer this question. Please get in touch with Hekades administrators to enhance my knowledge base."
        )

    def _setup_final_tag_selector(self, user_message: str) -> TagSelector:

        class Tag(BaseModel):
            tag_content: str
            tag_score: int

        class Tags(TagSelectorResponseModel):
            tag_list: list[Tag] = Field(
                default=[]
            )

            def get_tags(self):
                return [tag.tag_content for tag in self.tag_list if tag.tag_score >= 4]

        prompt = FINAL_TAG_SELECTION_PROMPT.format(tags="{tags}", question=user_message)
        extraction_prompt = """
        You are given a scoring of tags. Your job is to correctly extract the tags and their score.
        """

        return TagSelector(self.logger, self.moderate_model, self.cheap_model, tag_selection_prompt=prompt,
                           extraction_prompt=extraction_prompt, response_model=Tags)
