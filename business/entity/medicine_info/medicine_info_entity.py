from pydantic import BaseModel


class MedicineInfoEntity(BaseModel):
    name: str
    active_substance_name: str
    company_name: str
    kub_link: str
    sut: str
