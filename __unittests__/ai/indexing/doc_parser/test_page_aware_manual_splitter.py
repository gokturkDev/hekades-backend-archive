import pytest
from llama_index.core import Document

from ai.indexing.doc_parser.page_aware_manual_splitter import PageAwareManualSplitterNodeParser

text_1 = (
    """
    {&1&}
    ✅Geralt of Rivia was a legendary witcher of the School of the Wolf active throughout the 13th century. He loved the sorceress Yennefer, considered the love of his life despite their tumultuous relationship, and became Ciri's adoptive father. ✅.
    ✅
    During the Trial of the Grasses, Geralt exhibited unusual tolerance for the mutagens that grant witchers their abilities. Accordingly, Geralt was subjected to further experimental mutagens which rendered his hair white and may have given him greater speed, strength, and stamina than his fellow witchers.  
    ✅.  
    {&2&}
    ✅
    Despite his title, Geralt did not hail from the city of Rivia. After being left with the witchers by his mother, Visenna, he grew up in their keep of Kaer Morhen in the realm of Kaedwen. In the interest of appearing more trustworthy to potential clients, young witchers were encouraged to make up surnames for themselves by master Vesemir. As his first choice, Geralt chose "Geralt Roger Eric du Haute-Bellegarde", but this choice was dismissed by Vesemir as silly and pretentious, so "Geralt" was all that remained of his chosen name. "Of Rivia" was a more practical alternative and Geralt even went so far as to adopt a Rivian accent to appear more authentic. Later, Queen Meve of Lyria knighted him for his valor in the Battle for the Bridge on the Yaruga conferring on him the formal title "of Rivia", which amused him.[1] He, therefore, became a true knight. ✅.
    """
)

text_2 = (
    """
    {&22&}
    ✅Only one sentence✅.
    """
)


@pytest.mark.parametrize(
    "text,expected_chunk_count,page_chunk_dist", [
        (text_1, 3, {1: 2, 2: 1}),
        (text_2, 1, {22: 1})
    ]
)
def test_page_aware_manual_splitter(text, expected_chunk_count, page_chunk_dist):
    document = Document(text=text)
    node_parser = PageAwareManualSplitterNodeParser()
    nodes = node_parser.get_nodes_from_documents([document], show_progress=False)

    assert len(nodes) == expected_chunk_count
    for node in nodes:
        for page_number in node.metadata["page_numbers"]:
            assert page_number in page_chunk_dist
            page_chunk_dist[page_number] -= 1
    assert all([count == 0 for count in page_chunk_dist.values()])


fail_texts = [
    """
    {&22&}
    ✅ Yennefer of Vengerberg, born as Janka on Belleteyn in 1173, was a sorceress who lived in Vengerberg, \
     the capital city of Aedirn 
    """,
    """
    ✅She helped advise King Demavend of Aedirn\
     (though was never a formal royal advisor), ✅was a close friend of Triss Merigold,\
      and the youngest member of the Council of Wizards within the Brotherhood of Sorcerers.✅.               
    """,
    """
    ✅She was Geralt of Rivia's true love and a mother figure to Ciri, whom she viewed like a daughter ✅.
    ✅.to the point that she did everything she could to rescue the girl and keep her from harm.✅.              
    """,
    """
    After its fall, the Lodge of Sorceresses attempted to recruit her, but they didn't see eye to eye as the\
     Lodge wanted to advance their own political agenda by using Ciri
    """

]


@pytest.mark.parametrize("text", fail_texts)
def test_fails_on_bad_annotation(text):
    document = Document(text=text)
    node_parser = PageAwareManualSplitterNodeParser()

    with pytest.raises(ValueError):
        node_parser.get_nodes_from_documents([document], show_progress=False)
