import base64
from typing import Iterator

from core.utils.file import File


RES_PROMPT = """
You are an expert clinican. Your task is to analyse the image in detail and perfectly extract all data. Keep the format in image. Please always respond in Turkish and only output the data, no other words or explanations is needed.

"""

class ResourceSummarizer:

    def __init__(self, openai_client):
        self.openai_client = openai_client
        self.prompt = RES_PROMPT

    def summarize_resource(self, img_file: File) -> Iterator[str]:
        img_file.file_io.seek(0)
        base64_image = base64.b64encode(img_file.file_io.read()).decode('utf-8')

        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": self.prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            stream=True
        )
        for message in response:
            if message.choices[0].delta.content:
                yield message.choices[0].delta.content
