import pytest
from dotenv import load_dotenv

from ai.models.gpt_models.gpt_model import OpenAIModel
from ai.models.tools.math import add, substitute, multiply, divide, round_number

load_dotenv()


@pytest.mark.asyncio
async def test_function_calling():
    model = OpenAIModel(tools=[add, substitute, multiply, divide, round_number])

    stream = model.get_token_stream(
        prompt="Calculate the BMI of a person with weight 70 kgs and height 170cm. Calculate up to 6 digits")
    generated_answer = ""
    async for token in stream:
        generated_answer += token

    assert generated_answer
    print(generated_answer)
