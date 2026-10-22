import textwrap
from typing import List

from llama_index.core import Document
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.core.schema import TextNode

test_markdown_content = textwrap.dedent(
    """
    # Header 1
    ## Header 2
    b
    ## Header 3
    c
    ## Header 4
    d
    """
).strip()


def parse_markdown_to_text_nodes() -> List[TextNode]:
    markdown_node = Document(text=test_markdown_content)
    text_node_list = MarkdownNodeParser().get_nodes_from_node(markdown_node)
    return text_node_list


def test_markdown_node_parser_separates_headers():
    text_node_list = parse_markdown_to_text_nodes()

    assert len(text_node_list) == 4

    assert text_node_list[0].metadata["Header_1"] == "Header 1"

    assert text_node_list[1].metadata["Header_1"] == "Header 1"
    assert text_node_list[1].metadata["Header_2"] == "Header 2"

    assert text_node_list[2].metadata["Header_1"] == "Header 1"
    assert text_node_list[2].metadata["Header_2"] == "Header 3"

    assert text_node_list[3].metadata["Header_1"] == "Header 1"
    assert text_node_list[3].metadata["Header_2"] == "Header 4"


def test_markdown_node_parser_gets_content():
    text_node_list = parse_markdown_to_text_nodes()
    assert text_node_list[0].text == "Header 1"
    assert text_node_list[1].text == "Header 2\nb"
    assert text_node_list[2].text == "Header 3\nc"
    assert text_node_list[3].text == "Header 4\nd"
