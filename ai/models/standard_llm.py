from abc import ABC, abstractmethod
from typing import AsyncGenerator, AsyncIterable, Type, Optional

from pydantic import BaseModel


class StandardLLM(ABC):

    @abstractmethod
    def get_token_stream(self, prompt: str, additional_messages: Optional[list[dict]] = None,
                         user_msg: Optional[str] = None) -> \
            AsyncIterable[str]:
        pass

    @abstractmethod
    async def get_response(self, prompt: str, user_msg: Optional[str] = None) -> str:
        pass

    @abstractmethod
    async def get_response_with_response_model(self, user_msg: Optional[str], prompt: str,
                                               response_model: Type[BaseModel]) -> BaseModel:
        pass

    @abstractmethod
    async def get_streaming_response_with_response_model(self, prompt: str,
                                                         response_model: Type[BaseModel],
                                                         user_msg: Optional[str] = None) -> AsyncGenerator[
        BaseModel, None]:
        pass
