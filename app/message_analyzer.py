import spacy

nlp = spacy.load("es_core_news_sm")

mensaje = "¿Qué hace el pectoral superior?"
doc = nlp(mensaje)

for token in doc:
    print(token.text, token.lemma_, token.pos_, token.dep_)


