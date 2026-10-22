import uuid
from datetime import datetime
from typing import Optional

from business.entity.conversation.conversation_entity import ConversationEntity
from business.usecase.conversation.use_case_with_convo_repo import UsecaseWithConversationRepository


class StartConversationUsecase(UsecaseWithConversationRepository):
    def execute(self, title: str, user_email: str, patient_id: Optional[str] = None) -> ConversationEntity:
        if len(title) == 0 or len(user_email) == 0:
            raise ValueError("Title or user email cannot be empty")
        convo_uuid = str(uuid.uuid4())
        conversation = ConversationEntity(
            convo_id=convo_uuid,
            title=title,
            user_email=user_email,
            created_at=datetime.now(),
            patient_id=patient_id
        )
        self._repo.add(conversation)
        return conversation
