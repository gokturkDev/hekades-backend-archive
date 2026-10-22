import json
from __unittests__.interface.routers.test_router import TestRouter


class TestConversationRouter(TestRouter):
    @staticmethod
    async def _read_response_packets(response):
        response_packets_raw = response.read()
        response_packets = json.loads(response_packets_raw.decode())
        return response_packets

    @staticmethod
    def _get_ai_response_from_response_packets(response_packets) -> str:
        ai_response = ""
        for packet_raw in response_packets:
            packet = json.loads(packet_raw)
            token = packet["content"]
            ai_response += token
        return ai_response
