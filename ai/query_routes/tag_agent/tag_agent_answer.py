import asyncio
from typing import AsyncIterator, Optional

from ai.indexing.embedder.embedder import Embedder
from ai.models.standard_llm import StandardLLM
from ai.query_routes.tag_agent.prompts import QUERY_SCORING_PROMPT, TAG_AGENT_ANALYSIS_PROMPT, TAG_AGENT_ANSWER_PROMPT, \
    TAG_AGENT_QUERY_PROMPT
from ai.query_routes.utils.formats import format_source_chunks
from ai.retrieval.fusion.doc_aware_multilang_fusion_retriever import DocAwareMultilangFusionRetriever
from business.ai.ai_facade import ResponsePacket, ResponsePacketType
from core.lang.supported_lang import SupportedLanguages


class TagAgentAnswer:

    def __init__(self, tag, expensive_model: StandardLLM, cheap_model: StandardLLM, vector_index, logger,
                 embedder: Embedder,
                 record: str, language: SupportedLanguages) -> None:
        self.tag = tag
        self.ai_model = expensive_model
        self.logger = logger
        self.record = record
        self.language = language

        self.tag_agent_prompt = TAG_AGENT_ANSWER_PROMPT.format(tag="{tag}", context="{context}", analysis="{analysis}",
                                                               language=self.language.value)

        self.retriever = DocAwareMultilangFusionRetriever(ai_model=cheap_model, vector_index=vector_index,
                                                          logger=logger,
                                                          embedder=embedder, query_scoring_prompt=QUERY_SCORING_PROMPT,
                                                          rank_method="top_k")

    async def execute(self, query: str, rich_query: str, retrieval_queries: Optional[list[str]] = None) -> \
            AsyncIterator[ResponsePacket]:
        chunks, case_prez = None, self.record
        async with asyncio.TaskGroup() as tg:
            async def get_chunks():
                nonlocal chunks
                chunks = await self.retriever.retrieve(rich_query, [self.tag], retrieval_queries)

            tg.create_task(get_chunks())

        yield ResponsePacket(type=ResponsePacketType.STAGE_COMPLETED)
        yield ResponsePacket(type=ResponsePacketType.SOURCES, content=chunks)
        if not chunks:
            return
        
        tag_query = TAG_AGENT_QUERY_PROMPT.format(
            case_presentation=case_prez,
            query=query
        )

        analysis = await self.ai_model.get_response(prompt=TAG_AGENT_ANALYSIS_PROMPT, user_msg=tag_query)
        self.logger.info(f"Preliminary Analysis:\n{analysis}")
        yield ResponsePacket(type=ResponsePacketType.STAGE_COMPLETED)

        prompt = self.tag_agent_prompt.format(
            context=format_source_chunks(chunks),
            analysis=analysis,
            tag=self.tag

        )

        generated_answer = ""
        async for token in self.ai_model.get_token_stream(prompt, user_msg=tag_query):
            if token:
                generated_answer += token
                yield ResponsePacket(type=ResponsePacketType.TOKEN, content=token)

        self.logger.info(
            f"ANSWER {self.tag.upper()}\n\n\nCase Prez:\n\n\n{case_prez}\n\n\nPROMPT\n\n\n{prompt}\n\n\nANSWER\n\n\n{generated_answer}")
