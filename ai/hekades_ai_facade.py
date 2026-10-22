import json
import logging
import os
from typing import List, AsyncIterable, Optional

import boto3
import watchtower
from openai import OpenAI

from ai.indexing.embedder.embedder import Embedder
from ai.indexing.vector_index.vector_index import VectorIndex
from ai.models.aws_models.cohere_command_r_model import CohereCommandRModel
from ai.models.standard_llm import StandardLLM
from ai.prompts import RAW_PATIENT_RECORD_SUMMARIZER_PROMPT, \
    TRANSLATION_PROMPT, PUBMED_SUMMARIZATION_PROMPT, \
    PUBMED_SUMMARIZATION_WITH_RECORD_PROMPT
from ai.query_routes.case.case_query_route import CaseQueryRoute
from ai.query_routes.information.information_query_route import InformationQueryRoute
from ai.query_routes.off_topic.off_topic_query_route import OffTopicQueryRoute
from ai.query_routes.query_route import QueryRoute
from ai.query_type_classifier import QueryTypeClassifier
from ai.retrieval.pubmed.pubmed_retriever import PubmedRetriever, PubmedArticle
from ai.schemas import RouteName
from business.ai.ai_facade import AIFacade, ResponsePacket, ResponsePacketType
from business.entity.conversation.message_entity import MessageEntity
from business.entity.patient.patient_entity import PatientEntity
from business.repository.medicine_info.medicine_info_repository import MedicineInfoRepository
from core.lang.supported_lang import SupportedLanguages

file_path = os.path.join(os.path.dirname(__file__), 'stages.json')

with open(file_path, 'r', encoding='utf-8') as file:
    STAGES = json.load(file)


class HekadesAIFacade(AIFacade):
    def __init__(self, expensive_model: StandardLLM, expensive_instruct_model: StandardLLM,
                 rag_model: CohereCommandRModel, moderate_model: StandardLLM,
                 cheap_model: StandardLLM, vector_index: VectorIndex, medicine_info_repo: MedicineInfoRepository,
                 embedder: Embedder):
        self.expensive_model = expensive_model
        self.expensive_instruct_model = expensive_instruct_model
        self.rag_model = rag_model
        self.moderate_model = moderate_model
        self.cheap_model = cheap_model
        self.vector_index = vector_index
        self.medicine_info_repo = medicine_info_repo
        self.embedder = embedder

    async def respond_to_user(self, chat_history: List[MessageEntity], convo_id: str, user_message: str,
                              language: SupportedLanguages, patient: Optional[PatientEntity] = None) -> \
            AsyncIterable[ResponsePacket]:

        logger = self._setup_question_logger(convo_id)
        logger.info(f"Doctor question is {user_message}")
        user_message = await self.expensive_model.get_response(prompt=TRANSLATION_PROMPT, user_msg=user_message)
        logger.info(f"Doctor question translated as {user_message}")

        route_name = await QueryTypeClassifier.get_query_route_name(user_message, self.expensive_model, patient)
        yield ResponsePacket(type=ResponsePacketType.QUESTION_TYPE, content=route_name.value)
        logger.info("Route selected as " + route_name.value)

        if route_name.value == RouteName.INFORMATION.value:
            yield ResponsePacket(type=ResponsePacketType.STAGES, content=STAGES["information"][language.value])

        elif route_name.value == RouteName.CASE.value:
            yield ResponsePacket(type=ResponsePacketType.STAGES, content=STAGES["case"][language.value])

        query_route = self._get_query_route(route_name, logger, language, patient.patient_summary if patient else None)
        async for value in query_route.run(chat_history, user_message):
            yield value

    async def pubmed_search(self, convo_id: str, user_message: str, language: SupportedLanguages,
                            patient: Optional[PatientEntity] = None) -> \
            AsyncIterable[
                ResponsePacket]:
        logger = self._setup_pubmed_logger(convo_id)
        route_name = await QueryTypeClassifier.get_query_route_name(user_message, self.expensive_model, patient)

        if not route_name == RouteName.CASE and not route_name == RouteName.INFORMATION:
            return

        yield ResponsePacket(type=ResponsePacketType.STAGES, content=STAGES["pubmed"][language.value])

        logger.info("Retrieving literature from PubMed...")
        if patient:
            patient = await self.summarize_patient_record(patient)

        async for response in PubmedRetriever(self.expensive_model, self.cheap_model, self.embedder, logger, route_name,
                                              patient).retrieve(
            user_message):
            if isinstance(response, ResponsePacket):
                yield response
            else:
                pubmed_retrieved_articles = response

        if len(pubmed_retrieved_articles) == 0:
            yield ResponsePacket(type=ResponsePacketType.LITERATURE_SUMMARY_TOKEN,
                                 content=await self.cheap_model.get_response(
                                     f"Translate the following text to {language.value} and ONLY OUTPUT THE TRANSLATED TEXT:\n'An error happened while searching the literature.'"))

        yield ResponsePacket(type=ResponsePacketType.LITERATURE_DOCUMENTS,
                             content=[article.model_dump() for article in pubmed_retrieved_articles])

        async for token in self._summarize_articles(user_message, pubmed_retrieved_articles, logger, language, patient):
            if token is not None:
                yield ResponsePacket(type=ResponsePacketType.LITERATURE_SUMMARY_TOKEN, content=token)

    def _get_query_route(self, route_name: RouteName, logger, language, patient) -> QueryRoute:
        if route_name == RouteName.INFORMATION:
            return InformationQueryRoute(
                expensive_model=self.expensive_model,
                moderate_model=self.moderate_model,
                cheap_model=self.cheap_model,
                vector_index=self.vector_index,
                medicine_info_repo=self.medicine_info_repo,
                logger=logger,
                embedder=self.embedder,
                language=language,
                patient_record=patient
            )
        elif route_name == RouteName.CASE:
            return CaseQueryRoute(
                expensive_model=self.expensive_model,
                expensive_instruct_model=self.expensive_instruct_model,
                rag_model=self.rag_model,
                moderate_model=self.moderate_model,
                cheap_model=self.cheap_model,
                vector_index=self.vector_index,
                medicine_info_repo=self.medicine_info_repo,
                logger=logger,
                embedder=self.embedder,
                language=language,
                patient_record=patient
            )
        elif route_name == RouteName.OFF_TOPIC:
            return OffTopicQueryRoute(
                cheap_model=self.cheap_model,
            )
        else:
            raise ValueError(f"Invalid route name: {route_name}")

    def _setup_question_logger(self, convo_id: str):
        return self._setup_file_logger(convo_id, "q")

    def _setup_pubmed_logger(self, convo_id: str):
        return self._setup_file_logger(convo_id, "p")

    def _setup_file_logger(self, convo_id, prefix):
        logger = logging.getLogger(f"{prefix}-{convo_id}")
        logger.setLevel(logging.INFO)
        logger.addHandler(logging.FileHandler(f"logs/{prefix}-{convo_id}.log", encoding="utf-8"))
        if os.environ.get("AWS_LOGS_ACTIVE"):
            logger.addHandler(watchtower.CloudWatchLogHandler(boto3_client=boto3.client(
                "logs",
                region_name="eu-north-1")))
        logger.propagate = False
        return logger

    async def _summarize_articles(self, query: str, articles: List[PubmedArticle], logger, language: SupportedLanguages,
                                  patient: Optional[str]) -> \
            AsyncIterable[str]:

        abstracts_str = ""
        for i, article in enumerate(articles, start=1):
            abstracts_str += f"Abstract {i}. {article.abstract}\n"

        logger.info("Summarizing Pubmed Articles")

        if patient:
            prompt = PUBMED_SUMMARIZATION_WITH_RECORD_PROMPT.format(
                abstracts_str=abstracts_str,
                query=query,
                patient_record=patient,
                language=language.value
            )
        else:
            prompt = PUBMED_SUMMARIZATION_PROMPT.format(
                abstracts_str=abstracts_str,
                query=query,
                language=language.value
            )

        async for token in self.expensive_model.get_token_stream(user_msg=query, prompt=prompt):
            if token is not None:
                yield token

    async def summarize_patient_record(self, patient_record) -> str:
        processed_record_prompt = RAW_PATIENT_RECORD_SUMMARIZER_PROMPT.format_map({
            "patient_record": patient_record
        })

        processed_record = await self.expensive_model.get_response(processed_record_prompt)
        return processed_record
