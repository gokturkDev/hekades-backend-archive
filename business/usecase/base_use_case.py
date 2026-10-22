from abc import ABC, abstractmethod


class BaseUsecase(ABC):
    @abstractmethod
    def execute(self, *args, **kwargs):
        pass