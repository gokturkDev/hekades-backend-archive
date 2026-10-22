from abc import ABC, abstractmethod

from business.entity.patient.patient_entity import PatientEntity
from business.repository.base_repository import BaseRepository


class PatientRepository(BaseRepository, ABC):

    @abstractmethod
    def get_all_patients(self, user_id: str) -> list[PatientEntity]:
        pass

    @abstractmethod
    def get_patient(self, patient_id: str) -> PatientEntity:
        pass

    @abstractmethod
    def add_patient(self, patient: PatientEntity):
        pass

    @abstractmethod
    def update_patient(self, patient: PatientEntity):
        pass

    @abstractmethod
    def delete_patient(self, patient_id: str):
        pass
