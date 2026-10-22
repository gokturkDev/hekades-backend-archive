import inspect
import json
import re
from typing import AsyncGenerator, AsyncIterable, Type, Optional, Callable, Union

import instructor
from openai import NotGiven
from pydantic import BaseModel

from ai.models.standard_llm import StandardLLM


class OpenAIModel(StandardLLM):
    def __init__(self, client, model_name: str, temperature=0.1, max_tokens: int = 4095,
                 tools: Optional[list[Callable]] = None):
        """Tools are supported only for token streams for now"""
        self.client = client
        self.temperature = temperature
        self.instructor_client = instructor.from_openai(self.client)
        self.model_name = model_name
        self.max_tokens = max_tokens
        if tools:
            self.tools = tools
            self.tool_desc = [self.parse_docstring(fun) for fun in self.tools]

    async def get_token_stream(self, prompt: str, additional_messages: Optional[list[dict]] = None,
                               user_msg: Optional[str] = None) -> \
            AsyncIterable[str]:

        messages = await self._get_messages(additional_messages, prompt, user_msg)

        response_stream = await self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            tools=self.tool_desc if self.tool_desc else NotGiven,
            stream=True,
            temperature=0.1,
            top_p=0.7,
            seed=77,
            max_tokens=self.max_tokens
        )

        tool_calls = []

        async for token in self._read_stream_with_tool_calls(additional_messages, prompt, response_stream, tool_calls,
                                                             user_msg):
            yield token

    async def get_response(self, prompt: str, user_msg: Optional[str] = None) -> str:
        messages = await self._get_messages(None, prompt, user_msg)
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=0.1,
            top_p=0.7,
            seed=77
        )
        return response.choices[0].message.content

    async def get_response_with_response_model(self, user_msg: Optional[str], prompt: str,
                                               response_model: Type[BaseModel]) -> BaseModel:
        messages = await self._get_messages(None, prompt, user_msg)
        return await self.instructor_client.chat.completions.create(
            model=self.model_name,
            response_model=response_model,
            messages=messages,
            temperature=0.1,
            top_p=0.7,
            seed=77
        )

    async def get_streaming_response_with_response_model(self, prompt: str, response_model: Type[BaseModel],
                                                         user_msg: Optional[str] = None) -> AsyncGenerator[
        BaseModel, None]:
        messages = await self._get_messages(None, prompt, user_msg)
        return self.instructor_client.chat.completions.create_partial(
            model=self.model_name,
            response_model=response_model,
            messages=messages,
            temperature=0.1,
            top_p=0.7,
            seed=77
        )

    def _get_available_functions(self):
        available_funcs = {}

        for tool in self.tools:
            available_funcs[tool.__name__] = tool

        return available_funcs

    @staticmethod
    def parse_docstring(function):
        """
        Parse the docstring of a function to extract function name, description and parameters.

        Parameters
        ----------
        function : Callable
            The function whose docstring is to be parsed.

        Returns
        -------
        dict
            A dictionary with the function's name, description, and parameters.
        """
        doc = inspect.getdoc(function)

        # Find function description
        function_description = re.search(r'(.*?)Parameters', doc, re.DOTALL).group(1).strip()

        # Find parameter descriptions
        parameters_description = re.findall(r'(\w+)\s*:\s*(\w+)\n(.*?)(?=\n\w+\s*:\s*|\nReturns|$)', doc, re.DOTALL)

        # Get the parameters from the function signature
        signature_params = list(inspect.signature(function).parameters.keys())

        # Construct the parameters dictionary
        properties = {}
        required = []
        for name, type, description in parameters_description:
            name = name.strip()
            type = type.strip()
            description = description.strip()

            required.append(name)
            properties[name] = {
                "type": type,
                "description": description,
            }

        # Check if the number of parameters match
        if len(signature_params) != len(required):
            raise ValueError(
                f"Number of parameters in function signature ({len(signature_params)}) does not match the number of parameters in docstring ({len(required)})")

        # Check if each parameter in the signature has a docstring
        for param in signature_params:
            if param not in required:
                raise ValueError(f"Parameter '{param}' in function signature is missing in the docstring")

        parameters = {
            "type": "object",
            "properties": properties,
            "required": required,
        }

        # Construct the function dictionary
        function_dict = {
            "type": "function",
            "function": {
                "name": function.__name__,
                "description": function_description,
                "parameters": parameters
            }

        }

        return function_dict

    async def _read_stream_with_tool_calls(self, additional_messages, prompt, response_stream, tool_calls, user_msg):
        async for chunk in response_stream:
            delta = chunk.choices[0].delta

            if delta and delta.content:
                yield delta.content

            elif delta and delta.tool_calls:
                tc_chunk_list = delta.tool_calls
                for tc_chunk in tc_chunk_list:
                    await self._add_tool_call_data_from_chunk(tc_chunk, tool_calls)

            if chunk.choices[0].finish_reason == "tool_calls":
                messages = additional_messages if additional_messages else []
                messages.append({"role": "assistant", "tool_calls": tool_calls})

                for tool_call in tool_calls:
                    await self._add_tool_result_message(messages, tool_call)
                async for token in self.get_token_stream(prompt=prompt, additional_messages=messages,
                                                         user_msg=user_msg):
                    yield token

    async def _add_tool_result_message(self, messages, tool_call):
        available_functions = self._get_available_functions()
        function_name = tool_call['function']['name']
        if function_name not in available_functions:
            function_response = "Tool name is malformed, please try again with the correct tool name!"
        else:
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call['function']['arguments'])
            function_response = function_to_call(**function_args)
        messages.append(
            {
                "tool_call_id": tool_call['id'],
                "role": "tool",
                "name": function_name,
                "content": str(function_response),
            }
        )

    async def _add_tool_call_data_from_chunk(self, tc_chunk, tool_calls):
        if len(tool_calls) <= tc_chunk.index:
            tool_calls.append({"id": "", "type": "function", "function": {"name": "", "arguments": ""}})
        tc = tool_calls[tc_chunk.index]
        if tc_chunk.id:
            tc["id"] += tc_chunk.id
        if tc_chunk.function.name:
            tc["function"]["name"] += tc_chunk.function.name
        if tc_chunk.function.arguments:
            tc["function"]["arguments"] += tc_chunk.function.arguments

    async def _get_messages(self, additional_messages: Union[list[dict], None], prompt: str, user_msg: Optional[str]):
        messages = [{"role": "system", "content": prompt}]
        if user_msg:
            messages.append({"role": "user", "content": user_msg})
        if additional_messages:
            messages.extend(additional_messages)
        return messages
