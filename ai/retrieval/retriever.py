from abc import ABC, abstractmethod


class Retriever(ABC):

    @abstractmethod
    async def retrieve(self, query: str):
        pass
