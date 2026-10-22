from typing import List

from business.entity.conversation.message_entity import MessageEntity
from business.usecase.conversation.use_case_with_convo_repo import UsecaseWithConversationRepository


class GetMessagesOfConversationUsecase(UsecaseWithConversationRepository):

    def execute(self, convo_id: str) -> List[MessageEntity]:
        return self._repo.get_conversation_messages(convo_id)
