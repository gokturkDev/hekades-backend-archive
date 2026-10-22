import asyncio
import logging
from typing import override, Sequence, Any, List

from llama_index.core.node_parser import NodeParser
from llama_index.core.schema import TextNode

from ai.indexing.doc_parser.utils import gather_with_concurrency
from ai.models.standard_llm import StandardLLM

logger = logging.getLogger("hekades")

SUMMARIZER_PROMPT = """
Given the text below, your task is to create a concise and informative summary of each text. 
The summaries should capture the key information and main points discussed in the text. 
These summaries will be used to semantically match questions from doctors, so ensure they are detailed enough to capture the essence of the information while being concise.

Requirements for the Summaries:
- Clarity: Use clear and precise language that can easily be understood by medical professionals.
- Key Points: Highlight the main topics, important findings, or critical instructions presented on the text.
- Specificity: Include specific terms, conditions, treatments, or procedures mentioned in the text.
- Semantic Matching: The summary should be detailed enough to semantically match questions from doctors. Think about the questions a doctor can answer using this text and append them to the summary as well.

The summary MUST be in English! ONLY ENGLISH SUMMARIES WILL BE ACCEPTED!
Only output the summary.

Text:
{text}
Summary:
"""


class ChunkSummarizer(NodeParser):
    ai_model: StandardLLM

    @override
    def _parse_nodes(
            self,
            nodes: Sequence[TextNode],
            show_progress: bool = False,
            **kwargs: Any,
    ) -> List[TextNode]:
        logger.info("Summarizing chunks...")

        loop = asyncio.new_event_loop()
        loop.run_until_complete(self._add_summaries_to_nodes(nodes))

        return nodes

    async def _add_summaries_to_nodes(self, nodes: Sequence[TextNode]):
        async def add_summary(node):
            text = node.text
            summary = await self.ai_model.get_response(prompt=SUMMARIZER_PROMPT.format(text=text))
            node.metadata["hekades_summary"] = summary

        await gather_with_concurrency(200, *[add_summary(node) for node in nodes])
