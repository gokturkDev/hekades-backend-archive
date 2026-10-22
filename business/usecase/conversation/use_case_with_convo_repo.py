from abc import ABC

from business.repository.conversation.conversation_repository import ConversationRepository
from business.usecase.use_case_with_domain_repo import UsecaseWithDomainRepo


class UsecaseWithConversationRepository(UsecaseWithDomainRepo, ABC):

    def __init__(self, convo_repo: ConversationRepository):
        super().__init__(convo_repo)
        self._repo: ConversationRepository = convo_repo
