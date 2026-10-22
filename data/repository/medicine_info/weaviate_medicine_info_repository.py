from weaviate import WeaviateClient
from weaviate.classes.query import Filter

from business.entity.medicine_info.medicine_info_entity import MedicineInfoEntity
from business.repository.medicine_info.medicine_info_repository import MedicineInfoRepository
from data.helpers.weaviate_utils_mixin import WeaviateUtilsMixin
from data.repository.medicine_info.medicine_info_collection import create_medicine_info_collection


class WeaviateMedicineInfoRepository(MedicineInfoRepository, WeaviateUtilsMixin):

    def __init__(self, client: WeaviateClient):
        self.client = client
        self.collection_name = "medicine_info"

        if not self.client.collections.exists(self.collection_name):
            create_medicine_info_collection(self.client)

        self.collection = self.client.collections.get(self.collection_name)

    def add(self, medicine_infos: list[MedicineInfoEntity]):
        with self.collection.batch.dynamic() as batch:
            for medicine_info in medicine_infos:
                batch.add_object(
                    properties={
                        "active_substance_name": medicine_info.active_substance_name,
                        "name": medicine_info.name,
                        "company_name": medicine_info.company_name,
                        "kub_link": medicine_info.kub_link,
                        "sut": medicine_info.sut
                    }
                )

    def get_by_atc_name_semantic_search(self, query: str) -> list[MedicineInfoEntity]:
        def near_text_query():
            return self.collection.query.near_text(
                query=query,
                limit=1,
                target_vector="active_substance_name",  # Specify the target vector for named vector collections
            )

        response = self._query_with_retry(near_text_query, retry=5)
        o = response.objects[0]
        active_substance_name = o.properties["active_substance_name"]

        response = self.collection.query.fetch_objects(
            filters=Filter.by_property("active_substance_name").equal(active_substance_name),
            limit=100
        )

        return [MedicineInfoEntity(
            name=o.properties["name"],
            active_substance_name=o.properties["active_substance_name"],
            company_name=o.properties["company_name"],
            kub_link=o.properties["kub_link"],
            sut=o.properties["sut"]
        ) for o in response.objects]

    def get_by_atc_code(self, atc_code: str) -> list[MedicineInfoEntity]:
        pass
