import logging
import re
from dataclasses import dataclass
from typing import List

import nltk

tokenizer = nltk.tokenize.PunktSentenceTokenizer()
page_pattern = r"\{&\d+&\}"
logger = logging.getLogger("hekades")


@dataclass
class PageAwareSentence:
    text: str
    page_number: int


def get_page_nums_from_sentence(text: str) -> List[int]:
    matches = re.findall(page_pattern, text)
    page_nums = [int(match[1:-1].split('&')[1]) for match in matches]
    return page_nums


def page_aware_sentence_split(text: str) -> List[PageAwareSentence]:
    spans = list(tokenizer.span_tokenize(text))
    sentences = []
    current_page = 1
    for i, span in enumerate(spans):
        sentence = _get_text_between_start_end(i, span, spans, text)
        page_nums = get_page_nums_from_sentence(sentence)

        if len(page_nums) == 1:
            current_page = page_nums[0]
        elif len(page_nums) > 1:
            logger.warning(
                f"Multiple page numbers found in a single sentence: {sentence}. This is normally not allowed, but compensating by using the last one.")
            current_page = page_nums[-1]

        cleaned_sentence = re.sub(page_pattern, '', sentence)
        page_aware_sentence = PageAwareSentence(cleaned_sentence, current_page)

        sentences.append(page_aware_sentence)

    return sentences


# get the spans and then return the sentences
# using the start index of each span
# instead of using end, use the start of the next span if available
def _get_text_between_start_end(i, span, spans, text):
    start = span[0]
    if i < len(spans) - 1:
        end = spans[i + 1][0]
    else:
        end = len(text)
    sentence = text[start:end]
    return sentence
