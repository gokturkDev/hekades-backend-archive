from typing import List, AsyncIterable

from ai.query_routes.query_route import QueryRoute
from business.ai.ai_facade import ResponsePacket, ResponsePacketType
from business.entity.conversation.message_entity import MessageEntity

OFF_TOPIC_PROMPT = """
You are Hekades, an assistant AI for medical professionals.
A doctor has asked you a question however their question has been flagged as off topic.
Politely explain that their question isn't a question that you can answer.
Then, explain that you can only answer questions that are related to medical guidelines.
Respond to the doctor in a way that is professional and respectful.
ALWAYS respond in Turkish
"""


class OffTopicQueryRoute(QueryRoute):

    def __init__(self, cheap_model):
        self.cheap_model = cheap_model

    async def run(self, chat_history: List[MessageEntity], user_message: str) -> AsyncIterable[ResponsePacket]:
        async for token in self.cheap_model.get_token_stream(prompt=OFF_TOPIC_PROMPT, user_msg=user_message):
            yield ResponsePacket(content=token, type=ResponsePacketType.TOKEN)
