import asyncio
import json
import logging
from typing import AsyncGenerator, Type, Optional, AsyncIterable

from pydantic import BaseModel

from ai.models.aws_models.aws_model import AWSModel
from ai.models.standard_llm import StandardLLM

logger = logging.getLogger("hekades")


class LLamaModel(StandardLLM, AWSModel):

    def __init__(self, model_id, backup_model: StandardLLM):
        # Backup is needed because aws bedrock models are not always available
        self.backup_model = backup_model
        super().__init__(model_id)

    async def get_response_with_response_model(self, user_msg: str, prompt: str,
                                               response_model: Type[BaseModel]) -> BaseModel:
        raise NotImplementedError("This method is not implemented for the LLama model")

    async def get_streaming_response_with_response_model(self, prompt: str, response_model: Type[BaseModel],
                                                         user_msg: str = None) -> AsyncGenerator[BaseModel, None]:
        raise NotImplementedError("This method is not implemented for the LLama model")

    def _get_native_prompt(self, prompt: str, user_msg: str = None):
        return f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
        {prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>
        {user_msg}<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""

    def _get_request(self, prompt, user_msg, streaming: Optional[bool] = False):
        prompt = self._get_native_prompt(prompt, user_msg)
        native_request = {
            "prompt": prompt,
            "max_gen_len": 2048,
            "temperature": 0.3
        }
        return native_request

    async def get_response(self, prompt: str, user_msg: str = None) -> str:
        try:
            request = json.dumps(self._get_request(prompt, user_msg))
            response = await asyncio.to_thread(self.client.invoke_model, modelId=self.model_id, body=request)
            model_response = json.loads(response["body"].read())

            response_text = model_response["generation"]
            return response_text
        except Exception as e:
            logger.error(f"Error in LLamaModel.get_response, using backup model: {e}")
            return await self.backup_model.get_response(prompt, user_msg)

    async def get_token_stream(self, prompt: str, additional_messages: list[dict] = None, user_msg: str = None) -> \
            AsyncIterable[str]:
        try:
            request = json.dumps(self._get_request(prompt, user_msg))
            streaming_response = self.client.invoke_model_with_response_stream(
                modelId=self.model_id, body=request
            )

            for event in streaming_response["body"]:
                chunk = json.loads(event["chunk"]["bytes"])
                if "generation" in chunk:
                    if chunk["generation"]:
                        yield chunk["generation"]
        except Exception as e:
            logger.error(f"Error in LLamaModel.get_token_stream, using backup model: {e}")
            async for response in self.backup_model.get_token_stream(prompt, additional_messages, user_msg):
                yield response
