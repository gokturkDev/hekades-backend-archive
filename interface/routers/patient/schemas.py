from pydantic import BaseModel


class PatientAddModel(BaseModel):
    patient_name: str
    last_visit_date: str
    patient_file_text: str
