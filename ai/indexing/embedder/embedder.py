from abc import ABC, abstractmethod


class Embedder(ABC):

    @abstractmethod
    def embed(self, inputs: list[str], verbose=False, batch_size: int = 3) -> list[list[float]]:
        pass
