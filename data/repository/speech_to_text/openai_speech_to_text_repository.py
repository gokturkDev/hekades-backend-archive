import os
import uuid

from openai import OpenAI
from openai.types.audio import Transcription

from business.repository.speech_to_text.speech_to_text_repository import SpeechToTextRepository


class OpenAISpeechToTextRepository(SpeechToTextRepository):
    def __init__(self):
        super().__init__()
        self._client = OpenAI()

    def create_transcript(self, data: bytes) -> str:
        rand_id = f"{str(uuid.uuid4())}.wav"
        with open(rand_id, mode='bx') as f:
            f.write(data)

        audio_file = open(rand_id, "rb")
        transcription: Transcription = self._client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
        )
        os.remove(rand_id)
        return transcription.text
