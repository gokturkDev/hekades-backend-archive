from abc import ABC, abstractmethod

from business.repository.base_repository import BaseRepository


class SpeechToTextRepository(BaseRepository, ABC):
    @abstractmethod
    def create_transcript(self, data: bytes) -> str:
        pass
