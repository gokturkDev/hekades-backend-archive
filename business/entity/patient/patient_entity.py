import datetime

from pydantic import BaseModel


class PatientEntity(BaseModel):
    patient_id: str
    user_id: str
    patient_name: str
    last_visit_date: datetime.datetime
    patient_file_text: str
    patient_summary: str
