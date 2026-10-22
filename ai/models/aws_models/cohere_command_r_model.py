import asyncio
import json
from typing import Type, Optional, AsyncGenerator, AsyncIterable, Union, TypedDict

from pydantic import BaseModel

from ai.models.aws_models.aws_model import AWSModel


class CohereDocumentDict(TypedDict):
    title: str
    snippet: str


class CohereCommandRModel(AWSModel):

    async def get_token_stream(self, prompt: str, user_msg: str, documents: list[CohereDocumentDict]) -> \
            AsyncIterable[str]:
        body = self._get_request_body(prompt, user_msg, documents=documents)

        response = await asyncio.to_thread(self.client.invoke_model_with_response_stream,
                                           modelId=self.model_id,
                                           body=body
                                           )

        stream = response.get('body')
        if stream:
            for event in stream:
                chunk = event.get('chunk')
                if chunk:
                    yield json.loads(chunk.get('bytes').decode())

    async def get_response(self, prompt: str, user_msg: str, documents: list[CohereDocumentDict]) -> Union[
        str, dict]:
        body = self._get_request_body(prompt, user_msg, documents=documents)

        response = await asyncio.to_thread(self.client.invoke_model, body=body, modelId=self.model_id)
        response_body = json.loads(response.get('body').read())

        return {
            "text": response_body.get("text"),
            "citations": response_body.get("citations")
        }

    async def get_response_with_response_model(self, user_msg: Optional[str], prompt: str,
                                               response_model: Type[BaseModel],
                                               documents: Optional[str] = None) -> BaseModel:
        raise NotImplementedError("Not implemented")

    async def get_streaming_response_with_response_model(self, prompt: str, response_model: Type[BaseModel],
                                                         user_msg: Optional[str] = None,
                                                         documents: Optional[str] = None) -> AsyncGenerator[
        BaseModel, None]:
        raise NotImplementedError("Not implemented")

    def _get_request_body(self, prompt: str, user_msg: str, stream: bool = False,
                          documents: Optional[list[dict]] = None):
        prompt = f"# System Prompt\n{prompt}\n# User Message\n{user_msg}"

        body = {
            "message": prompt,
            "chat_history": [],
            "documents": documents if documents else [],
            "max_tokens": 2000,
            "temperature": 0.6,
            "p": 0.5,
            "k": 250
        }
        return json.dumps(body)
