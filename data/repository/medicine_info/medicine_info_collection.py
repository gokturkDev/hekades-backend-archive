from weaviate import WeaviateClient
from weaviate.classes.config import Configure, Property, DataType, Tokenization
from weaviate.collections.classes import config


def create_medicine_info_collection(client: WeaviateClient):
    client.collections.create(
        "medicine_info",
        properties=[
            Property(
                name="active_substance_name",
                data_type=DataType.TEXT,
                tokenization=Tokenization.FIELD
            ),
            Property(
                name="name",
                data_type=DataType.TEXT,
                skip_vectorization=True,
                tokenization=Tokenization.FIELD
            ),
            Property(
                name="company_name",
                data_type=DataType.TEXT,
                skip_vectorization=True,
                tokenization=Tokenization.FIELD
            ),
            Property(
                name="kub_link",
                data_type=DataType.TEXT,
                skip_vectorization=True,
                tokenization=Tokenization.FIELD
            ),
            Property(
                name="sut",
                data_type=DataType.TEXT,
                skip_vectorization=True,
                tokenization=Tokenization.FIELD
            )
        ],
        vectorizer_config=[
            Configure.NamedVectors.text2vec_openai(
                name="active_substance_name", source_properties=["active_substance_name"],
                vector_index_config=config.Configure.VectorIndex.hnsw(ef=1000)
            )
        ]
    )
