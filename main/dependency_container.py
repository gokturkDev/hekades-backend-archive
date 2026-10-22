import json
import logging
import os
from abc import abstractmethod
from os.path import join, dirname
from typing import override

import boto3
import openai
import sendgrid
import weaviate
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from sendgrid import sendgrid
from twilio.rest import Client

from ai.hekades_ai_facade import HekadesAIFacade
from ai.indexing.embedder.infinity_embedder import InfinityEmbedder
from ai.indexing.resource_summarization.resource_summarizer import ResourceSummarizer
from ai.indexing.source_indexer import SourceIndexer
from ai.indexing.vector_index.vector_index import VectorIndex
from ai.models.aws_models.cohere_command_r_model import CohereCommandRModel
from ai.models.aws_models.llama_model import LLamaModel
from ai.models.gpt_models.gpt_model import OpenAIModel
from ai.models.tools.math import add, substitute, multiply, divide, round_number
from business.ai.ai_facade import AIFacade as IAIFacade
from business.ai.source_indexer import SourceIndexer as ISourceIndexer
from business.repository.conversation.conversation_repository import ConversationRepository as IConversationRepository
from business.repository.medicine_info.medicine_info_repository import MedicineInfoRepository as IMedicineInfoRepository
from business.repository.patient.patient_repository import PatientRepository as IPatientRepository
from business.repository.source.chunk_resource_repository import ChunkResourceRepository as IChunkResourceRepository
from business.repository.source.source_repository import SourceRepository as ISourceRepository
from business.repository.speech_to_text.speech_to_text_repository import SpeechToTextRepository
from business.repository.user.user_repository import UserRepository as IUserRepository
from data.indexing.vector_index.weaviate_vector_index import WeaviateVectorIndex
from data.repository.conversation.dynamo_conversation_repository import DynamoDBConversationRepository
from data.repository.medicine_info.weaviate_medicine_info_repository import WeaviateMedicineInfoRepository
from data.repository.patient.dynamo_patient_repository import DynamoPatientRepository
from data.repository.source.facade_source_repository import FacadeSourceRepository
from data.repository.source.s3_chunk_resource_repository import S3ChunkResourceRepository
from data.repository.source.source_display_file_repository.s3_source_display_file_repository import \
    S3SourceDisplayFileRepository
from data.repository.source.source_info_repository.dynamo_source_info_repo import DynamoSourceInfoRepository
from data.repository.speech_to_text.openai_speech_to_text_repository import OpenAISpeechToTextRepository
from data.repository.user.dynamo_user_repository import DynamoUserRepository

logger = logging.getLogger("hekades")


class DepContainer:
    convo_repo: IConversationRepository
    ai_facade: IAIFacade
    source_repo: ISourceRepository
    user_repo: IUserRepository
    chunk_resource_repo: IChunkResourceRepository
    medicine_info_repo: IMedicineInfoRepository
    patient_repo: IPatientRepository
    source_indexer: ISourceIndexer
    vector_index: VectorIndex
    resource_summarizer: ResourceSummarizer
    twilio_client: Client
    stt_client: SpeechToTextRepository
    sendgrid_client: sendgrid.SendGridAPIClient

    @classmethod
    @abstractmethod
    def initialize_dependencies(cls):
        pass


class DepContainerImpl(DepContainer):

    @classmethod
    @override
    def initialize_dependencies(cls):
        load_dotenv(dotenv_path=join(dirname(__file__), ".env"))
        cls.load_secrets_from_aws()
        cls.convo_repo = DynamoDBConversationRepository()
        gpt4_o = OpenAIModel(client=openai.AsyncOpenAI(), temperature=0, model_name="gpt-4o",
                             tools=[add, substitute, multiply, divide, round_number])
        gpt4_o_mini = OpenAIModel(client=openai.AsyncOpenAI(), temperature=0, model_name="gpt-4o-mini",
                                  tools=[add, substitute, multiply, divide, round_number])
        command_r_plus = CohereCommandRModel(model_id="cohere.command-r-plus-v1:0")
        llama_70_model = LLamaModel("meta.llama3-1-70b-instruct-v1:0", backup_model=gpt4_o_mini)
        llama_405_model = LLamaModel("meta.llama3-1-405b-instruct-v1:0", backup_model=gpt4_o)

        weaviate_auth = weaviate.auth.AuthApiKey(os.environ.get("WCS_API_KEY"))
        wv_client = weaviate.connect_to_wcs(
            cluster_url=os.environ.get("WCS_URL"),
            auth_credentials=weaviate_auth,
            headers={'X-OpenAI-Api-key': os.environ.get("OPENAI_API_KEY")},
            skip_init_checks=True
        )

        embedder = InfinityEmbedder(
            embedding_service_url=os.environ.get("INFINITY_SERVER_URL"),
            embedding_service_api_key=os.environ.get("INFINITY_API_KEY")
        )

        cls.vector_index = WeaviateVectorIndex(
            client=wv_client,
            embedder=embedder
        )

        cls.ai_facade = HekadesAIFacade(
            expensive_model=gpt4_o,
            rag_model=command_r_plus,
            expensive_instruct_model=llama_405_model,
            moderate_model=llama_70_model,
            cheap_model=gpt4_o_mini,
            vector_index=cls.vector_index,
            medicine_info_repo=WeaviateMedicineInfoRepository(client=wv_client),
            embedder=embedder
        )
        cls.source_repo = FacadeSourceRepository(
            source_display_file_repository=S3SourceDisplayFileRepository(),
            source_info_repo=DynamoSourceInfoRepository()
        )
        cls.user_repo = DynamoUserRepository()
        cls.patient_repo = DynamoPatientRepository()
        cls.sendgrid_client = sendgrid.SendGridAPIClient(api_key=os.environ.get("SENDGRID_API_KEY"))

        cls.stt_client = OpenAISpeechToTextRepository()

        cls.chunk_resource_repo = S3ChunkResourceRepository()
        cls.source_indexer = SourceIndexer(
            vector_index=cls.vector_index,
            chunk_resource_repo=cls.chunk_resource_repo,
            openai_client=openai.OpenAI(),
            ai_model=gpt4_o,
        )
        cls.medicine_info_repo = WeaviateMedicineInfoRepository(client=wv_client)

        cls.resource_summarizer = ResourceSummarizer(openai_client=openai.OpenAI())
        cls.twilio_client = Client(os.environ.get("TWILIO_ACCOUNT_SID"),
                                   os.environ.get("TWILIO_AUTH_TOKEN"))
        cls.sendgrid_client = sendgrid.SendGridAPIClient(api_key=os.environ.get("SENDGRID_API_KEY"))

    @staticmethod
    def load_secrets_from_aws():
        logger.info("Loading secrets from AWS...")
        if os.environ.get("AWS_SECRET_NAME") is not None:
            session = boto3.session.Session()
            client = session.client(
                service_name='secretsmanager',
                region_name=os.environ.get("AWS_SECRET_REGION"),
            )
            try:
                secrets = json.loads(
                    client.get_secret_value(SecretId=os.environ.get("AWS_SECRET_NAME"))["SecretString"])
            except ClientError as e:
                logger.error("Error loading secrets from AWS", exc_info=e)

            def set_if_exists(secret_name: str):
                if secret_name in secrets:
                    os.environ[secret_name] = secrets[secret_name]

            set_if_exists("OPENAI_API_KEY")
            set_if_exists("WCS_API_KEY")
            set_if_exists("WCS_URL")
            set_if_exists("NCBI_API_KEY")
            set_if_exists("NCBI_EMAIL")
            set_if_exists("AUTH_SECRET_KEY")
            set_if_exists("TWILIO_ACCOUNT_SID")
            set_if_exists("TWILIO_AUTH_TOKEN")
            set_if_exists("TWILIO_VERIFY_SERVICE_SID")
            set_if_exists("SENDGRID_API_KEY")
            set_if_exists("INFINITY_SERVER_URL")
            set_if_exists("INFINITY_API_KEY")
        else:
            print("AWS_SECRET_NAME not set, skipping loading secrets from AWS")
