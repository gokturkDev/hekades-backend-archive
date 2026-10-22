from typing import Iterator

from business.ai.ai_facade import ResponsePacket, ResponsePacketType


def stream_response(string: str) -> Iterator[ResponsePacket]:
    for i in string:
        yield ResponsePacket(
            type=ResponsePacketType.TOKEN,
            content=i
        )


def stream_string(string: str) -> Iterator[str]:
    for i in string:
        yield i
