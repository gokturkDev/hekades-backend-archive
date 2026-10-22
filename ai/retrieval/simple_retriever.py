from ai.indexing.vector_index.vector_index import VectorIndex
from ai.retrieval.retriever import Retriever


class SimpleRetriever(Retriever):
    def __init__(self, vector_index: VectorIndex):
        self.vector_index = vector_index

    def retrieve(self, query: str):
        return self.vector_index.semantic_search(query, 20)
