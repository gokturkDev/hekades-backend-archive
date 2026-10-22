import base64
import io
import logging
import os
import uuid

from openai import OpenAI
from unstructured_client import UnstructuredClient
from unstructured_client.models import shared

from ai.indexing.indexing_pipeline.indexing_pipeline import IndexingPipeline
from ai.indexing.vector_index.vector_index import VectorIndex
from business.entity.source.source_chunk import SourceChunk
from business.entity.source.source_entity import SourceEntity
from business.repository.source.chunk_resource_repository import ChunkResourceRepository
from core.utils.file import File

logger = logging.getLogger("hekades")


class PDFFileIndexingPipeline(IndexingPipeline):

    def __init__(self, vector_index: VectorIndex, chunk_resource_repo: ChunkResourceRepository, openai_client: OpenAI):
        super().__init__(vector_index=vector_index)
        self.chunk_resource_repo = chunk_resource_repo
        self.openai_client = openai_client
        self.unstructured_client = UnstructuredClient(
            api_key_auth=os.environ.get("UNSTRUCTURED_API_KEY"),
            server_url=os.environ.get("UNSTRUCTURED_SERVER_URL")
        )

    def run(self, source: SourceEntity):
        logger.info(f"Parsing pdf file for {source.info.name}")
        source_file = source.file
        pdf_elements = self._parse_pdf(source_file)
        logger.info(f"PDF parsed for {source.info.name}")

        chunks = []
        logger.info(f"Creating chunks for {source.info.name}")
        logger.info(f"Creating text chunks for {source.info.name}")
        chunks.extend(self._get_text_chunks_from_pdf_elements(pdf_elements, source.info.id))
        logger.info(f"Creating resource chunks for {source.info.name}")
        chunks.extend(self._create_chunks_with_resource(pdf_elements, source.info.id))

        self.vector_index.index_chunks(chunks)

    def _parse_pdf(self, source_file: File) -> list[dict]:
        files = shared.Files(
            content=source_file.file_io.read(),
            file_name=source_file.filename
        )
        req = shared.PartitionParameters(
            files=files,
            strategy="auto",
            extract_image_block_types=["Image", "Table"],
            pdf_infer_table_structure=True
        )
        response = self.unstructured_client.general.partition(req)
        return response.elements

    @staticmethod
    def _get_text_chunks_from_pdf_elements(pdf_elements: list[dict], source_id: str) -> list[SourceChunk]:
        chunks = []
        for elem in pdf_elements:
            if elem["type"] == "NarrativeText":
                text = elem["text"]
                chunks.append(SourceChunk(
                    content=text,
                    source_id=source_id,
                    chunk_id=str(uuid.uuid4()),
                    metadata={
                        "page_number": elem["metadata"]["page_number"],
                        "has_resource": False
                    }
                ))
        return chunks

    def _create_chunks_with_resource(self, pdf_elems: list[dict], source_id: str) -> list[SourceChunk]:
        chunks = []
        for elem in pdf_elems:
            if elem["type"] == "Image" or elem["type"] == "Table":
                chunk = self._create_chunk_with_resource(elem, source_id)
                chunks.append(chunk)
        return chunks

    def _create_chunk_with_resource(self, elem: dict, source_id: str) -> SourceChunk:
        chunk_id = str(uuid.uuid4())
        img_io = self._get_elem_img_as_io(elem)
        file = File(file_io=img_io, filename=f"{chunk_id}.png")

        self.chunk_resource_repo.store_chunk_resource(source_id, chunk_id, file)
        resource_url = self.chunk_resource_repo.get_chunk_resource_url(source_id, chunk_id)
        summarization = self._summarize_resource(resource_url)

        return SourceChunk(
            source_id=source_id,
            content=summarization,
            chunk_id=chunk_id,
            metadata={
                "page_number": elem["metadata"]["page_number"],
                "has_resource": True
            }
        )

    def _summarize_resource(self, resource_url: str) -> str:
        prompt = """
            Please analyze the image and convert its information into a detailed, cohesive paragraph.\
            Ensure that all information in the image, such as text, numbers, symbols, abbreviations, shapes, arrows and other visual elements, is included and no details are omitted.\
            Structure the paragraph as follows:\
            1. Describe each element in the image, providing all relevant information for each one, and explain the context in which each element relates to other elements.\
            2. Conclude with an article that discusses any patterns, notable points and all important insights derived from the items in the image
        """
        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text",
                         "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": resource_url
                            },
                        },
                    ],
                }
            ],
            max_tokens=2000,
        )
        return response.choices[0].message.content

    @staticmethod
    def _get_elem_img_as_io(elem: dict) -> io.BytesIO:
        image = elem["metadata"]["image_base64"]
        image_data = base64.b64decode(image)
        return io.BytesIO(image_data)
