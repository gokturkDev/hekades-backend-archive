import json
import os
from datetime import datetime

import pytest

from __test_utils__.mock_dependency_container import MockDepContainer
from __unittests__.interface.routers.conversation.test_conversation_router import TestConversationRouter
from business.entity.conversation.message_entity import UserMessageEntity, SystemMessageEntity


class TestGetMessagesOfConversation(TestConversationRouter):
    def setup_method(self):
        super().setup_method()
        self.test_convo_id = "123"
        self._create_dummy_messages_for_conversation()
        MockDepContainer.convo_repo.get_conversation_by_id.return_value.user_email = os.environ.get("TEST_USER_EMAIL")

    def _create_dummy_messages_for_conversation(self):
        MockDepContainer.convo_repo.get_conversation_messages.return_value = [
            UserMessageEntity(content="Hello", convo_id=self.test_convo_id, order=1, created_at=datetime.now()),
            SystemMessageEntity(content="Hello World!", convo_id=self.test_convo_id, order=2, created_at=datetime.now(),
                                citations={})
        ]

    @pytest.mark.asyncio
    async def test_get_messages_of_conversation(self):
        response = self._query_get_messages_of_conversation_endpoint(test_convo_id=self.test_convo_id)

        assert response.status_code == 200

        messages_packet = await self._read_response_packets(response)
        assert messages_packet is not None
        message_dict = json.loads(messages_packet)

        assert len(message_dict) == 2
        assert message_dict['1']['content'] == "Hello"
        assert message_dict['2']['content'] == "Hello World!"

    def _query_get_messages_of_conversation_endpoint(self, test_convo_id: str):
        response = self.client.get(
            f'/conversation/{test_convo_id}'
        )
        return response
