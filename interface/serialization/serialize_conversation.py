from typing import List

from business.entity.conversation.conversation_entity import ConversationEntity
from business.entity.conversation.message_entity import MessageEntity


def serialize_conversation_entities(entities: List[ConversationEntity]):
    serialized_conversations = {}
    for entity in entities:
        serialized_conversations[str(entity.convo_id)] = entity.model_dump()
    return serialized_conversations


def serialize_message_entities(entities: List[MessageEntity]):
    serialized_messages = {}
    for entity in entities:
        serialized_msg = entity.model_dump()
        serialized_messages[str(entity.order)] = serialized_msg
    return serialized_messages
