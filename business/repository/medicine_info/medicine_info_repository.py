from abc import ABC, abstractmethod

from business.entity.medicine_info.medicine_info_entity import MedicineInfoEntity


class MedicineInfoRepository(ABC):

    @abstractmethod
    def add(self, medicine_infos: list[MedicineInfoEntity]):
        pass

    @abstractmethod
    def get_by_atc_code(self, atc_code: str) -> list[MedicineInfoEntity]:
        pass

    @abstractmethod
    def get_by_atc_name_semantic_search(self, query: str) -> list[MedicineInfoEntity]:
        pass
