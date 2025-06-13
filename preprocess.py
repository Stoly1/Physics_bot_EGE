import spacy

nlp = spacy.load("ru_core_news_sm")

def preprocess_text(text):
    doc = nlp(text.lower())
    tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
    return " ".join(tokens)

if __name__ == "__main__":
    sample = "Как решить задачу на закон сохранения энергии?"
    print(preprocess_text(sample))