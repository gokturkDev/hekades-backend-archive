import json
from datetime import datetime

import pytest

from __test_utils__.mock_dependency_container import MockDepContainer
from __unittests__.interface.routers.conversation.test_conversation_router import TestConversationRouter
from business.entity.conversation.conversation_entity import ConversationEntity


class TestGetConversations(TestConversationRouter):
    def setup_method(self):
        super().setup_method()
        self.test_user_email = "example@example.com"
        self._create_dummy_convos_for_user()

    def _create_dummy_convos_for_user(self):
        MockDepContainer.convo_repo.get_conversations_of_user.return_value = [
            ConversationEntity(convo_id="123", title="Test 1", user_email=self.test_user_email,
                               created_at=datetime.now()),
            ConversationEntity(convo_id="345", title="Test 2", user_email=self.test_user_email,
                               created_at=datetime.now())
        ]

    @pytest.mark.asyncio
    async def test_get_conversations_from_user_email(self):
        response = self._query_get_conversations_endpoint(test_user_email=self.test_user_email)

        assert response.status_code == 200

        conversations_packet = await self._read_response_packets(response)
        assert conversations_packet is not None
        conversation_dict = json.loads(conversations_packet)

        assert len(conversation_dict) == 2
        assert conversation_dict['123']['title'] == "Test 1"
        assert conversation_dict['345']['title'] == "Test 2"

    def _query_get_conversations_endpoint(self, test_user_email: str):
        response = self.client.get(
            '/conversation/all'
        )
        return response
