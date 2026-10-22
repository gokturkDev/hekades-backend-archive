from datetime import datetime

from business.entity.conversation.message_entity import UserMessageEntity
from business.usecase.conversation.use_case_with_convo_repo import UsecaseWithConversationRepository


class AddUserMessageUsecase(UsecaseWithConversationRepository):

    def execute(self, convo_id, content, created_at=datetime.now()):
        if not convo_id or not content:
            raise ValueError("Convo ID and Content must not be empty")

        order = self._get_latest_order(convo_id) + 1

        message = UserMessageEntity(
            convo_id=convo_id,
            content=content,
            order=order,
            created_at=created_at
        )
        self._repo.add_message(message)

    def _get_latest_order(self, convo_id):
        latest_msg = self._repo.get_latest_message(convo_id)
        if latest_msg:
            return latest_msg.order
        else:
            return 0
