from typing import List

from llama_index.core import Document
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import TextNode

pipeline = IngestionPipeline(
    transformations=[
        SentenceSplitter(chunk_size=25, chunk_overlap=0),
    ]
)


def test_sentence_splitter():
    document = Document.example()

    nodes: List[TextNode] = pipeline.run(documents=[document])
    assert nodes
    text = ""
    for node in nodes:
        text += node.text
    # Remove all whitespaces because the text is split into chunks on sentences
    # and the whitespaces might not match the original text
    assert ''.join(text.split()) == ''.join(document.text.split())
