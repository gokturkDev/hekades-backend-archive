from typing import List

from business.entity.conversation.conversation_entity import ConversationEntity
from business.usecase.conversation.use_case_with_convo_repo import UsecaseWithConversationRepository


class GetConversationsOfUserUsecase(UsecaseWithConversationRepository):
    def execute(self, user_email: str) -> List[ConversationEntity]:
        return self._repo.get_conversations_of_user(user_email)
