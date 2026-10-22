from unittest.mock import Mock

from ai.indexing.resource_summarization.resource_summarizer import ResourceSummarizer
from ai.indexing.vector_index.vector_index import VectorIndex
from business.ai.ai_facade import AIFacade
from business.ai.source_indexer import SourceIndexer
from business.repository.conversation.conversation_repository import ConversationRepository
from business.repository.source.source_repository import SourceRepository
from business.repository.user.user_repository import UserRepository
from interface.auth.auth import setup_auth
from main.dependency_container import DepContainer


class MockDepContainer(DepContainer):
    user_repo: Mock
    convo_repo: Mock
    source_repo: Mock
    source_indexer: Mock
    vector_index: Mock
    resource_summarizer: Mock
    ai_facade: Mock

    @classmethod
    def initialize_dependencies(cls):
        setup_auth()
        cls.user_repo = Mock(spec=UserRepository)
        cls.convo_repo = Mock(spec=ConversationRepository)
        cls.source_repo = Mock(spec=SourceRepository)
        cls.source_indexer = Mock(spec=SourceIndexer)
        cls.vector_index = Mock(spec=VectorIndex)
        cls.resource_summarizer = Mock(spec=ResourceSummarizer)
        cls.ai_facade = Mock(spec=AIFacade)

    @classmethod
    def reset_mocks(cls):
        cls.user_repo.reset_mock()
        cls.convo_repo.reset_mock()
        cls.source_repo.reset_mock()
        cls.source_indexer.reset_mock()
        cls.vector_index.reset_mock()
        cls.resource_summarizer.reset_mock()
        cls.ai_facade.reset_mock()
