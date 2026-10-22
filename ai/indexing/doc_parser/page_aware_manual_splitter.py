import copy
import logging
from typing import override, Sequence, List, Any

from llama_index.core.node_parser import NodeParser
from llama_index.core.schema import BaseNode, Document, TextNode
from llama_index.core.utils import get_tqdm_iterable

from ai.indexing.doc_parser.page_aware_sentence_splitter import page_aware_sentence_split

chunk_symbol = "✅"
chunk_close_symbol = "✅."  # This is a convention for getting the best results.
# Chunk Checker checks for this however chunking doesn't care about the dot

logger = logging.getLogger("hekades")


class PageAwareManualSplitterNodeParser(NodeParser):

    @override
    def _parse_nodes(
            self,
            nodes: Sequence[BaseNode],
            show_progress: bool = False,
            **kwargs: Any,
    ) -> List[BaseNode]:
        """Parse document into nodes."""
        all_nodes: List[BaseNode] = []
        nodes_with_progress = get_tqdm_iterable(nodes, show_progress, "Parsing nodes")

        for node in nodes_with_progress:
            nodes = self._build_nodes_from_documents([node])
            all_nodes.extend(nodes)

        return all_nodes

    def _build_nodes_from_documents(
            self,
            documents: Sequence[Document],
            show_progress: bool = False,
            **kwargs: Any
    ) -> List[TextNode]:
        all_nodes = []
        for doc in documents:
            text = doc.text
            errors = self.get_errors_in_annotation(text)
            if errors:
                logger.error('\n'.join(errors))
                raise ValueError("There are errors in annotation. Aborting indexing...")

            sentences = page_aware_sentence_split(text)
            nodes = self._get_nodes_from_sentences(sentences, doc)
            all_nodes.extend(nodes)

        return all_nodes

    @classmethod
    def _get_nodes_from_sentences(cls, sentences, document: Document):
        nodes = []
        cursor_on = False
        chunk_content = ""
        page_numbers = set()
        for sentence in sentences:
            page_numbers.add(sentence.page_number)
            for char in sentence.text:
                if char == chunk_symbol:
                    if cursor_on:
                        cursor_on = False
                        if cls._check_text_is_valid_chunk_text(chunk_content):
                            nodes.append(
                                cls._create_node(chunk_content, page_numbers, document)
                            )
                        page_numbers = set()
                        chunk_content = ""
                    else:
                        cursor_on = True
                    continue

                if cursor_on:
                    chunk_content += char
        return nodes

    @staticmethod
    def _create_node(text: str, page_numbers: set, document: Document) -> TextNode:
        metadata = copy.deepcopy(document.metadata)
        metadata["page_numbers"] = list(page_numbers)
        cleaned_text = text.strip()

        return TextNode(text=cleaned_text, metadata=metadata)

    @staticmethod
    def _check_text_is_valid_chunk_text(text: str):
        return len(text.replace("\n", "").replace(".", "").strip()) > 0

    @staticmethod
    def get_errors_in_annotation(text: str) -> list[str]:
        errors = []
        cursor_on = False
        captured_text = ""
        for i, line in enumerate(text.split("\n")):
            for j, char in enumerate(line):
                if char == chunk_symbol and (j + 1 != len(line) and line[j + 1] == "."):
                    if not cursor_on:
                        errors.append(f"Line: {i + 1}: Chunk closed without opening")
                    cursor_on = False
                elif char == chunk_symbol:
                    if cursor_on:
                        errors.append(f"Line: {i + 1}: New chunk symbol before chunk closed")
                    cursor_on = True

                if cursor_on:
                    captured_text += char

        if cursor_on:
            errors.append("Line LAST :Chunk closed without opening")

        lost_percentage = (len(text) - len(captured_text)) / len(text)

        if lost_percentage > 0.3 and lost_percentage < 0.6:
            logger.warning(
                "More than 30% of the text isn't captured. This is likely a mistake. Please check. Proceeding anyway")
        elif lost_percentage >= 0.6:
            errors.append("More than 60% of the text isn't captured. This is likely a mistake. Stopping indexing")

        return errors
