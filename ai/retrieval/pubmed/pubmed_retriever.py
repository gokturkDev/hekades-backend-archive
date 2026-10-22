import asyncio
import math
import os
from os.path import join, dirname
from typing import AsyncGenerator, AsyncIterable, List, Optional, Any, Union

from Bio import Entrez
from pydantic import BaseModel

from ai.indexing.embedder.embedder import Embedder
from ai.models.standard_llm import StandardLLM
from ai.retrieval.pubmed.prompts import ANALYSIS_PROMPT, ANALYSIS_WITH_RECORD_PROMPT, RERANKER_PROMPT, \
    RERANKER_WITH_RECORD_PROMPT, SEARCH_TERM_GENERATION_PROMPT, SEARCH_TERM_GENERATION_WITH_ANALYSIS_PROMPT, \
    SEARCH_TERM_GENERATION_WITH_RECORD_AND_ANALYSIS_PROMPT, TERM_EXTRACTOR_PROMPT
from ai.retrieval.retriever import Retriever
from ai.schemas import RouteName
from ai.utils.cosine_similarity import cosine_similarity_q_docs
from business.ai.ai_facade import ResponsePacket, ResponsePacketType
from business.entity.patient.patient_entity import PatientEntity


class PubmedArticle(BaseModel):
    pm_id: str
    language: str
    title: str
    journal: str
    abstract: Optional[str]
    date: Optional[str]
    score: Optional[float] = None


def _get_issn_numbers() -> List[str]:
    with open(join(dirname(__file__), "ISSNs.txt")) as f:
        return f.read().split("\n")


class BooleanSearchQueries(BaseModel):
    query_list: list[str]


class PubmedRetriever(Retriever):
    issn_numbers: List[str]

    def __init__(self, expensive_model: StandardLLM, cheap_model: StandardLLM, embedder: Embedder, logger,
                 route_name: RouteName, patient: Optional[str] = None):
        super().__init__()
        self.expensive_model = expensive_model
        self.cheap_model = cheap_model
        self.embedder = embedder
        self.logger = logger
        self.patient = patient
        self.route_name = route_name
        self._setup_entrez()
        if not hasattr(PubmedRetriever, "issn_numbers"):
            PubmedRetriever.issn_numbers = _get_issn_numbers()

    async def retrieve(self, query: str) -> AsyncIterable[Union[List[PubmedArticle], ResponsePacket]]:
        search_terms = await self._generate_search_terms(query)
        yield ResponsePacket(type=ResponsePacketType.STAGE_COMPLETED)

        all_ids = set()

        iteration = 8
        num_iterations = math.ceil(len(search_terms) / iteration)
        for i in range(num_iterations):
            sublist = search_terms[i * iteration:(i + 1) * iteration]
            async with asyncio.TaskGroup() as tg:
                async def handle_search(term):
                    nonlocal all_ids
                    ids = await asyncio.to_thread(self._search_pubmed, term)
                    all_ids = all_ids.union(set(ids))

                for term in sublist:
                    tg.create_task(handle_search(term))

        yield ResponsePacket(type=ResponsePacketType.STAGE_COMPLETED)

        if len(all_ids) == 0:
            yield []

        articles = await asyncio.to_thread(self._fetch_articles_from_id, all_ids)
        self.logger.info(f"Retrieved {len(articles)} articles")

        self.logger.info("Reranking articles...")
        articles = await self._rerank_articles(query, articles)
        yield ResponsePacket(type=ResponsePacketType.STAGE_COMPLETED)

        articles = articles[:20]

        for i, article in enumerate(articles):
            self.logger.info(f"Article {i + 1}: {article.title}")

        yield articles

    async def _generate_search_terms(self, question: str) -> List[str]:

        if self.route_name == RouteName.INFORMATION:
            prompt = SEARCH_TERM_GENERATION_PROMPT.format(question=question)
        else:
            if self.patient:
                analysis = await self.expensive_model.get_response(
                    ANALYSIS_WITH_RECORD_PROMPT.format(record=self.patient), user_msg=question)
                self.logger.info(f"Analysis:\n{analysis}")
                prompt = SEARCH_TERM_GENERATION_WITH_RECORD_AND_ANALYSIS_PROMPT.format(record=self.patient,
                                                                                       question=question,
                                                                                       analysis=analysis)
            else:
                analysis = await self.expensive_model.get_response(ANALYSIS_PROMPT, user_msg=question)
                self.logger.info(f"Analysis:\n{analysis}")
                prompt = SEARCH_TERM_GENERATION_WITH_ANALYSIS_PROMPT.format(analysis=analysis, question=question)

        search_query_reasoning = await self.expensive_model.get_response(prompt=prompt)
        self.logger.info(f"Search Query Reasoning:\n{search_query_reasoning}")
        search_queries = await self.cheap_model.get_response_with_response_model(prompt=TERM_EXTRACTOR_PROMPT,
                                                                                 user_msg=search_query_reasoning,
                                                                                 response_model=BooleanSearchQueries)
        return search_queries.query_list

    def _search_pubmed(self, term: str) -> List[str]:
        query = self._get_entrez_query_from_search_term(term)
        self.logger.info(f"Searching PubMed for search term: {term}")

        handle = Entrez.esearch(db="pubmed", term=query, retmax=10, sort='relevance')
        record = Entrez.read(handle)
        handle.close()
        pm_ids = record["IdList"]
        self.logger.info(f"Found {len(pm_ids)} articles for search term: {term}")
        return pm_ids

    async def _rerank_articles(self, question: str, articles: List[PubmedArticle]) -> List[PubmedArticle]:
        article_vectors = self.embedder.embed(
            [article.abstract if article.abstract else article.title for article in articles], batch_size=10)

        if self.patient:
            prompt = RERANKER_WITH_RECORD_PROMPT.format(query=question, patient_record=self.patient)
        else:
            prompt = RERANKER_PROMPT.format(query=question)

        question_vector = self.embedder.embed([prompt])[0]

        cosine_sim = cosine_similarity_q_docs(question_vector, article_vectors)
        for sim, article in zip(cosine_sim, articles):
            article.score = sim

        return sorted(articles, key=lambda article: article.score, reverse=True)

    def _get_rerank_prompt(self, question):
        if self.patient:
            prompt = RERANKER_WITH_RECORD_PROMPT.format(
                patient_record=self.patient.patient_file_text,
                question=question
            )
        else:
            prompt = question

        return prompt

    @classmethod
    def _get_entrez_query_from_search_term(cls, search_term: str):
        return f"({' OR '.join([f"{issn}[TA]" for issn in cls.issn_numbers])}) AND ({search_term})"

    def _fetch_articles_from_id(self, id_list: list[str]) -> List[PubmedArticle]:
        self.logger.info(f"Fetching {len(id_list)} articles from PubMed")
        articles = []

        handle = Entrez.efetch(db='pubmed',
                               retmode='xml',
                               id=id_list)
        result = Entrez.read(handle)
        data_list = result["PubmedArticle"]
        for data in data_list:
            article = self._create_article_from_data(data)
            if article is not None:
                articles.append(article)
        return articles

    @staticmethod
    def _create_article_from_data(data: Any) -> Union[PubmedArticle, None]:
        id = data['MedlineCitation']['PMID']
        title = data['MedlineCitation']['Article']['ArticleTitle']
        if len(title.strip()) == 0:
            return None
        try:
            abstract = '\n'.join(data['MedlineCitation']['Article']['Abstract']['AbstractText'])
        except:
            abstract = None

        journal = data['MedlineCitation']['Article']['Journal']['Title']
        language = data['MedlineCitation']['Article']['Language'][0]
        try:
            year = data['MedlineCitation']['Article']['Journal']['JournalIssue']['PubDate']['Year']
            month = data['MedlineCitation']['Article']['Journal']['JournalIssue']['PubDate']['Month']
            date = f"{year}-{month}"
        except:
            date = None

        return PubmedArticle(
            pm_id=id,
            title=title,
            abstract=abstract,
            journal=journal,
            language=language,
            date=date
        )

    def _setup_entrez(self):
        ncbi_key = os.environ.get("NCBI_API_KEY")
        if ncbi_key is None:
            self.logger.warning("NCBI_API_KEY is not set. Please set it to avoid rate limiting.")
        else:
            Entrez.api_key = ncbi_key
        ncbi_email = os.environ.get("NCBI_EMAIL")
        if ncbi_email is None:
            self.logger.warning("NCBI_EMAIL is not set. Please set it to avoid rate limiting.")
        else:
            Entrez.email = ncbi_email
        Entrez.sleep_between_tries = 1
