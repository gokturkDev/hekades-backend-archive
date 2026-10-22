import pytest

from ai.indexing.doc_parser.page_aware_sentence_splitter import get_page_nums_from_sentence, page_aware_sentence_split


@pytest.mark.parametrize("sentence,real_page_nums", [
    ("This is a test sentence", []),
    ("This is page {&1&}", [1]),
    ("This a a page {&1&} and this is a page {&2&} too", [1, 2])
])
def test_extract_page_numbers_from_sentence(sentence, real_page_nums):
    extracted_page_numbers = get_page_nums_from_sentence(sentence)
    assert extracted_page_numbers == real_page_nums


test_text_1 = """
{&1&}
✅
The Conjunction of the Spheres was a cataclysm which affected the whole Multiverse and occurred 1,500 years before the events in the novels, trapping many "unnatural" creatures in this dimension, including ghouls, graveirs, and vampires. Rifts were created by the collision of many different realms, filling the world of the gnomes and dwarves with hundreds of creatures of all shapes and sizes, as well as a mystical force that came to be known as "chaos" or "magic". 
✅
{&2&}
✅
Unable to manipulate the forces of magic and with little preparation to fight the monsters that came through the conjunction of the different realms, the gnomes, dwarves, and elves, as well as many other displaced races such as the vran, werebbubbs, halflings, and the first humans, were plunged into a strange, dangerous, and uncertain time of conflict which lasted for many generations.
✅
Unable to manipulate the forces of magic and with little preparation to fight the monsters that came through the conjunction of the different realms, the gnomes, dwarves, and elves, as well as many other displaced races such as the vran, werebbubbs, halflings, and the first humans, were plunged into a strange, dangerous, and uncertain time of conflict which lasted for many generations.
✅
{&3&}
✅
It was during this time that the elves say humans, or more specifically, the Dauk and Wozgor people, first appeared, their own world having been destroyed. Nordling humans settled on the Continent many hundreds of years after that, which event was later dubbed the First Landing. It is uncertain whether or not the two original human civilizations were extinct by the time the Nordlings arrived on the Continent. 
✅
"""
test_text_2 = """
There should always be a first page but we got you covered.
{&2&}
You can't separate a sentence by page {&3&} oops but we can still handle it. 
"""


@pytest.mark.parametrize("text,sentence_count, real_sentence_page_dist", [
    (test_text_1, 8, {1: 2, 2: 2, 3: 4}),
    # Last one with the symbol is unfortunately taken as a sentence by nltk sentence model
    (test_text_2, 2, {1: 1, 3: 1})
])
def test_page_aware_sentence_splitter(text, sentence_count, real_sentence_page_dist):
    page_aware_sentences = page_aware_sentence_split(text)
    sentence_page_dist = {}

    for sentence in page_aware_sentences:
        if sentence.page_number not in sentence_page_dist:
            sentence_page_dist[sentence.page_number] = 0
        sentence_page_dist[sentence.page_number] += 1

    assert len(page_aware_sentences) == sentence_count
    assert sentence_page_dist == real_sentence_page_dist
