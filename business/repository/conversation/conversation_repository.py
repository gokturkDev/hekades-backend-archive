# File: business/repository/ConversationRepository.py

from abc import ABC, abstractmethod
from typing import List, Optional

from business.entity.conversation.conversation_entity import ConversationEntity
from business.entity.conversation.message_entity import MessageEntity, SystemMessageEntity
from business.repository.base_repository import BaseRepository


class ConversationRepository(BaseRepository, ABC):
    @abstractmethod
    def add(self, conversation: ConversationEntity):
        pass

    @abstractmethod
    def get_conversations_of_user(self, user_id: str) -> List[ConversationEntity]:
        pass

    @abstractmethod
    def get_conversation_by_id(self, convo_id: str) -> ConversationEntity:
        pass

    @abstractmethod
    def update_conversation(self, conversation: ConversationEntity):
        pass

    @abstractmethod
    def update_message(self, convo_id: str, message: SystemMessageEntity):
        pass

    @abstractmethod
    def add_message(self, message: MessageEntity):
        pass

    @abstractmethod
    def get_conversation_messages(self, convo_id: str) -> List[MessageEntity]:
        pass

    @abstractmethod
    def get_latest_message(self, convo_id: str) -> MessageEntity | None:
        pass
