from typing import Union
from pydantic import BaseModel, Field


class AssessmentForm(BaseModel):
    patient_information: Union[str, None] = Field(description="Age, gender")
    complaints: Union[str, None] = Field(description="In-depth report of the complaints of the patient.")
    history_of_present_illness: Union[str, None] = Field(
        description="Detailed account of the current medical issue, covering the onset, characteristics, and factors affecting the condition.")
    physical_examination: Union[str, None] = Field(
        description="Objective assessment including vital signs and a systematic examination of the patient's body systems.")
    diagnostic_tests_and_results: Union[str, None] = Field(
        description="The results of laboratory tests, imaging studies, and other diagnostic procedures.")

    @classmethod
    def get_headers_for_fields(cls) -> dict[str, str]:
        return {
            "patient_information": "Hasta Bilgileri",
            "complaints": "Şikayetler",
            "history_of_present_illness": "Mevcut Hastalığın Öyküsü",
            "physical_examination": "Fizik Muayene Bulguları",
            "diagnostic_tests_and_results": "Tanısal Testler ve Sonuçlar"
        }
