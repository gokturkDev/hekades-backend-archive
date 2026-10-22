import logging
from time import sleep

from weaviate.exceptions import WeaviateQueryError

logger = logging.getLogger("hekades")


class WeaviateUtilsMixin:

    @classmethod
    def _query_with_retry(cls, query, retry=5):
        try:
            response = query()
        except WeaviateQueryError as e:
            logger.error(f"Failed to query weaviate: {e}\nRetrying...")
            if retry > 0:
                sleep(0.5)
                return cls._query_with_retry(query, retry - 1)
            else:
                raise RuntimeError("Failed to query weaviate after 5 retries")
        return response
