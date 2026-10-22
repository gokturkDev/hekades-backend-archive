import os
from unittest.mock import call, ANY

import pytest

from __test_utils__.mock_dependency_container import MockDepContainer
from __test_utils__.mock_utils import stream_response
from __unittests__.interface.routers.conversation.test_conversation_router import TestConversationRouter
from business.entity.conversation.message_entity import MessageEntity, UserMessageEntity, SystemMessageEntity


class TestNewMessage(TestConversationRouter):

    def setup_method(self):
        super().setup_method()
        self.test_convo_id = "123"
        self.test_user_msg = "Hello"
        self.test_ai_response = "Hello World!"
        MockDepContainer.ai_facade.respond_to_user.return_value = stream_response(self.test_ai_response)
        MockDepContainer.convo_repo.get_latest_message.return_value = None
        MockDepContainer.convo_repo.get_conversation_by_id.return_value.user_email = os.environ.get("TEST_USER_EMAIL")

        def set_latest_message(message: MessageEntity):
            MockDepContainer.convo_repo.get_latest_message.return_value = message

        MockDepContainer.convo_repo.add_message.side_effect = set_latest_message

    @pytest.mark.asyncio
    async def test_new_message_conversation(self):
        response = self._query_new_message_endpoint(
            dummy_user_message=self.test_user_msg,
            conversation_id=self.test_convo_id
        )

        response_packets = []

        for packet in response.iter_lines():
            response_packets.append(packet)

        ai_response = self._get_ai_response_from_response_packets(response_packets)

        assert response.status_code == 200
        assert ai_response == self.test_ai_response

        self._assert_source_repo_was_correctly_called()

    def _assert_source_repo_was_correctly_called(self):
        expected_calls_to_source_repo = [
            call(
                UserMessageEntity(
                    content=self.test_user_msg,
                    convo_id=self.test_convo_id,
                    order=1,
                    created_at=ANY
                )
            ),
            call(
                SystemMessageEntity(
                    content=self.test_ai_response,
                    convo_id=self.test_convo_id,
                    order=2,
                    created_at=ANY,
                    citations={}
                )
            )]
        assert MockDepContainer.convo_repo.add_message.call_args_list == expected_calls_to_source_repo

    def _query_new_message_endpoint(self, dummy_user_message: str, conversation_id: str):
        response = self.client.post(
            f"/conversation/{conversation_id}",
            json={
                "content": dummy_user_message
            }
        )
        return response
