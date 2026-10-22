from fastapi import UploadFile

from business.usecase.speech_to_text.usecase_with_stt_repo import UsecaseWithSttRepository


class CreateTranscriptUsecase(UsecaseWithSttRepository):
    async def execute(self, data: UploadFile) -> str:
        return self._repo.create_transcript(data=await data.read())
