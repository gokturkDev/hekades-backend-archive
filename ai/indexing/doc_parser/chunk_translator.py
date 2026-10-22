import asyncio
from typing import override, Sequence, List, Any

import logging
from llama_index.core.node_parser import NodeParser
from llama_index.core.schema import TextNode
from fast_langdetect import detect

from ai.indexing.doc_parser.utils import gather_with_concurrency
from ai.models.standard_llm import StandardLLM

logger = logging.getLogger("hekades")

TRANSLATOR_PROMPT = """
**Prompt:**
Translate the following excerpt from Turkish medical guidelines into English. The translation should be precise, maintaining the original medical terminology and context. Ensure that any specialized terms or clinical instructions are translated accurately to preserve the intended meaning. Where necessary, provide a brief explanation of any culturally specific or context-sensitive terms to ensure clarity for an English-speaking audience.
**Turkish Excerpt:**
{text}
**Instructions:**
1. **Prioritize Accuracy**: Focus on precise translation of medical terms and clinical guidelines. Ensure that all technical language is accurately translated to retain the exact meaning as intended in the original text.
2. **Contextual Appropriateness**: The translation should be contextually appropriate for a professional medical audience. Maintain a formal and clinical tone, avoiding simplification or casual language.
3. **Handling Specialized Terms**: If a term does not have a direct English equivalent, provide the closest possible translation. Include a brief explanation in parentheses or as a footnote to clarify the term’s meaning. For example:
- Original: “Erişkin dönemde görülen hepatosteatoz...”
- Translation: “Hepatosteatosis observed in adulthood (a condition characterized by fat accumulation in the liver)...”
4. **Maintain Structure and Tone**: Retain the structure and tone of the original guideline. Ensure the translation is suitable for use in clinical or educational settings, preserving the instructional format and intent.
5. **Cultural and Context-Specific Terms**: Identify any culturally specific or context-sensitive terms. Provide a concise explanation to ensure understanding by an English-speaking audience unfamiliar with the Turkish healthcare context. For example, if the guideline references a specific practice unique to Turkey, explain its relevance briefly.
6. **Enhance Readability**: While maintaining technical accuracy, use synonyms where appropriate to avoid repetition and enhance readability. Ensure the translation remains clear and professional.
7. **Explanations for Contextual Terms**: Provide explanations for any terms or concepts that may be unfamiliar to an English-speaking audience. Keep explanations concise, focusing on providing just enough detail to aid understanding without overwhelming the reader.
By following these instructions, aim to produce a translation that accurately conveys the content, intent, and instructional value of the original Turkish medical guideline. Only output the translation
"""


class ChunkTranslator(NodeParser):
    ai_model: StandardLLM

    @override
    def _parse_nodes(
            self,
            nodes: Sequence[TextNode],
            show_progress: bool = False,
            **kwargs: Any,
    ) -> List[TextNode]:
        logger.info("Translating chunks...")

        loop = asyncio.new_event_loop()
        loop.run_until_complete(self._translate_nodes(nodes))

        return nodes

    async def _translate_nodes(self, nodes: Sequence[TextNode]):
        async def translate_node(node):
            language = detect(node.text, low_memory=False)["lang"]
            if not language == "en":
                text = node.text
                translation = await self.ai_model.get_response(prompt=TRANSLATOR_PROMPT.format(text=text))
                node.text = translation

        await gather_with_concurrency(200, *[translate_node(node) for node in nodes])
