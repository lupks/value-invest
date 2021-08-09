import spacy
from string import punctuation

nlp = spacy.load("en_core_web_lg")

def get_kw(text):
    result = []
    pos_tag = ['PROPN', 'ADJ', 'NOUN']  # 1
    doc = nlp(text.lower())  # 2
    for token in doc:
        # 3
        if (token.text in nlp.Defaults.stop_words or token.text in punctuation):
            continue
        # 4
        if (token.pos_ in pos_tag):
            result.append(token.text)

    return list(set(result))


