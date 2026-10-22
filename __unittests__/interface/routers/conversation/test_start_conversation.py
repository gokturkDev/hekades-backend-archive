import json
from typing import Iterable, AsyncIterable
from unittest.mock import ANY
import pytest
from fastapi import WebSocketDisconnect

from __test_utils__.mock_dependency_container import MockDepContainer
from __test_utils__.mock_utils import stream_response
from __unittests__.interface.routers.conversation.test_conversation_router import TestConversationRouter


class TestStartConversation(TestConversationRouter):
    def setup_method(self):
        super().setup_method()
        self.test_ai_response = "Hello World!"
        self.test_user_email = "example@example.com"
        self.test_user_msg = "Hello"
        MockDepContainer.ai_facade.respond_to_user.return_value = stream_response(self.test_ai_response)
        MockDepContainer.convo_repo.get_latest_message.return_value = None

    @pytest.mark.asyncio
    async def test_should_respond_with_convo_packet_first(self):
        print("HELLOOO")
        async for response_packet in self._query_start_endpoint(
                message=self.test_user_msg
        ):
            convo_packet = json.loads(
                response_packet
            )
            # Response is a dictionary where the convo ID is the key
            # ID is generated at runtime, so we get the first key
            convo_packet = convo_packet[next(iter(convo_packet))]
            assert convo_packet
            break

    @pytest.mark.asyncio
    async def test_should_respond_with_ai_response_after_convo_packet(self):
        is_getting_ai_response = False
        ai_response = ""
        async for response_packet in self._query_start_endpoint(
                message=self.test_user_msg
        ):
            # MockDepContainer.convo_repo.add.assert_called_once()
            # MockDepContainer.ai_facade.respond_to_user.assert_called_once_with(user_message=self.test_user_msg,
            #                                                                    chat_history=[],
            #                                                                    retrieval_strategy=ANY)
            response_packet = json.loads(response_packet)
            if response_packet["type"] == "token":
                is_getting_ai_response = True
                ai_response += response_packet["content"]
            else:
                if is_getting_ai_response:
                    break

        assert ai_response == self.test_ai_response

    async def _query_start_endpoint(self, message: str) -> AsyncIterable[str]:
        access_token = self.client.headers.get("Authorization").split(" ")[1]
        # for i in range(10):
        #     yield json.dumps({
        #         "type": "token",
        #         "content": "Hello World"
        #     })

        with self.client.websocket_connect(f"/conversation/?token={access_token}") as websocket:
            websocket.send_text("hello world")
            try:
                while True:
                    data = websocket.receive_json()
                    print("This is the data I received ", data)
                    yield data
            except WebSocketDisconnect:
                return
