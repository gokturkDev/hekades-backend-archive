from abc import ABC

from business.repository.speech_to_text.speech_to_text_repository import SpeechToTextRepository
from business.usecase.use_case_with_domain_repo import UsecaseWithDomainRepo


class UsecaseWithSttRepository(UsecaseWithDomainRepo, ABC):

    def __init__(self, stt_repo: SpeechToTextRepository):
        super().__init__(stt_repo)
        self._repo: SpeechToTextRepository = stt_repo
