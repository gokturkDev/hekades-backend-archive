import numpy as np
from numpy.linalg import norm


def cosine_similarity_q_docs(q_vector: list[float], doc_vectors: list[list[float]]) -> np.ndarray:
    q_vector = np.array(q_vector)
    doc_vectors = np.array(doc_vectors)

    return np.dot(doc_vectors, q_vector) / (norm(doc_vectors, axis=1) * norm(q_vector))

def cosine_similarity_v_v(q_vector: list[float], doc_vector: list[float]) -> float:
    q_vector = np.array(q_vector)
    doc_vector = np.array(doc_vector)

    return np.dot(doc_vector, q_vector) / (norm(doc_vector) * norm(q_vector))