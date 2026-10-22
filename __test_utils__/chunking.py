def text_word_equivalence(text1: str, text2: str) -> float:
    words1 = set(text1.split())
    words2 = set(text2.split())
    return len(words1 & words2) / len(words1 | words2)
