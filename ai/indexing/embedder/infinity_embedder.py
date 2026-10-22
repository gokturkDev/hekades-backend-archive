import json
import logging
from http.client import HTTPResponse
from urllib.error import HTTPError

from ai.indexing.embedder.embedder import Embedder
import urllib.request

from main.constants import EMBEDDING_MODEL_NAME

logger = logging.getLogger("hekades")


class InfinityEmbedder(Embedder):

    def __init__(self, embedding_service_url, embedding_service_api_key):
        self.embedding_service_url = embedding_service_url
        self.embedding_service_api_key = embedding_service_api_key

    def embed(self, inputs: list[str], verbose=False, batch_size: int = 3) -> list[list[float]]:
        if not self.embedding_service_url:
            raise ValueError("INFINITY_SERVER_URL environment variable not set")
        if not self.embedding_service_api_key:
            raise ValueError("INFINITY_SERVER_API_KEY environment variable not set")

        splitted_inputs = [inputs[i:i + batch_size] for i in range(0, len(inputs), batch_size)]

        embeddings = []
        for i, input in enumerate(splitted_inputs):
            if verbose:
                logger.info(f"Embedding batch {i + 1}")
            i_embeddings = self._get_embedding_for_inputs(input)
            if i_embeddings[0][0] is None:
                raise RuntimeError(f"Error embedding input {i}, none fields \n Content: {input}")

            embeddings.extend(i_embeddings)

        return embeddings

    def _get_embedding_for_inputs(self, inputs: list[str]) -> list[list[float]]:
        data = json.dumps({
            "model": EMBEDDING_MODEL_NAME,
            "input": inputs
        }).encode()

        headers = {
            "Authorization": "Bearer " + self.embedding_service_api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1"
        }
        request = urllib.request.Request(f"{self.embedding_service_url}/embeddings", data=data, headers=headers)
        try:
            response: HTTPResponse = urllib.request.urlopen(request)
        except HTTPError as e:
            if e.getcode() == 403:
                raise RuntimeError(
                    f"403 Forbidden error when trying to embed inputs: \n{str(inputs)}\nLength:{str(len("".join(inputs)))}\nThis is mostly likely due to sending more data than is allowed by the HTTP protocol.")
            else:
                raise e
        embeddings = []
        e_json = json.loads(response.read())
        e_data = e_json["data"]
        for e in e_data:
            embeddings.append(e["embedding"])

        return embeddings
