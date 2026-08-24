"""Feature engineering de texto para o classificador de temática de IA (v0)."""

from __future__ import annotations

from sklearn.feature_extraction.text import TfidfVectorizer

# Lista curada de stopwords em português. Não é um pacote de NLP externo
# (ex.: nltk/spacy com download de corpora) para manter o ambiente
# reprodutível offline sem depender de baixar um corpus em tempo de
# instalação — é uma lista estática, versionada como código, inspirada na
# cobertura de listas padrão de stopwords em PT-BR (artigos, preposições,
# pronomes, conjunções, formas comuns dos verbos ser/estar/ter/haver) mas
# revisada manualmente. Ampliada em relação à v0 original (que tinha ~70
# palavras) para reduzir ruído de termos puramente gramaticais no TF-IDF;
# ver docs/PRD.md, backlog de melhorias, item "stopwords".
STOPWORDS_PT_BASICO = [
    "a", "à", "ao", "aos", "as", "às", "com", "como", "da", "das", "de",
    "dela", "dele", "deles", "delas", "do", "dos", "e", "é", "em", "entre",
    "essa", "essas", "esse", "esses", "esta", "estas", "este", "estes",
    "eu", "foi", "foram", "há", "isso", "isto", "já", "lhe", "lhes", "mais",
    "mas", "me", "mesmo", "meu", "meus", "minha", "minhas", "muito", "na",
    "nas", "nem", "no", "nos", "nós", "nossa", "nossas", "nosso", "nossos",
    "num", "numa", "o", "os", "ou", "para", "pela", "pelas", "pelo", "pelos",
    "por", "qual", "quando", "que", "quem", "se", "sem", "ser", "seu",
    "seus", "só", "sua", "suas", "também", "te", "tem", "têm", "teu", "teus",
    "tu", "tua", "tuas", "um", "uma", "você", "vocês",
    # --- ampliação ---
    # artigos/pronomes/conectivos adicionais
    "aquela", "aquelas", "aquele", "aqueles", "aquilo", "cada", "elas",
    "ela", "ele", "eles", "essoutro", "meu", "nas", "nossa", "outra",
    "outras", "outro", "outros", "todas", "todo", "todos", "toda", "vos",
    "vosso", "vossa", "vossos", "vossas",
    # advérbios/quantificadores comuns, sem carga temática
    "agora", "ainda", "algum", "alguma", "algumas", "alguns", "ali", "além",
    "antes", "aqui", "assim", "atrás", "bem", "cima", "contra", "depois",
    "desde", "então", "logo", "mal", "menos", "nada", "nenhum", "nenhuma",
    "nunca", "onde", "outrem", "pois", "pouca", "pouco", "poucas", "poucos",
    "quanto", "quanta", "quantos", "quantas", "sempre", "sob", "sobre",
    "talvez", "tampouco", "tanto", "tão", "toda",
    # verbos auxiliares/copulativos (ser, estar, ter, haver) em formas
    # frequentes -- carregam pouco sinal temático num corpus jornalístico
    "sou", "somos", "são", "era", "eram", "será", "serão", "seria",
    "seriam", "estou", "está", "estamos", "estão", "estava", "estavam",
    "estará", "estarão", "esteve", "estive", "estivemos", "tenho", "tem",
    "temos", "tinha", "tinham", "terá", "terão", "teria", "teriam", "hei",
    "havia", "houve", "houver",
    # numerais por extenso (raramente discriminativos neste corpus)
    "um", "uma", "dois", "duas", "três", "quatro", "cinco",
    # marcadores de discurso jornalístico muito genéricos
    "segundo", "aos", "às", "the",
]
# Remove duplicatas mantendo a ordem (algumas entradas acima coincidem de
# propósito com a lista original, para deixar claro o que já existia).
STOPWORDS_PT_BASICO = list(dict.fromkeys(STOPWORDS_PT_BASICO))


def build_tfidf_vectorizer(
    max_features: int = 8000,
    ngram_range: tuple[int, int] = (1, 2),
    min_df: int = 2,
    sublinear_tf: bool = True,
) -> TfidfVectorizer:
    return TfidfVectorizer(
        max_features=max_features,
        ngram_range=tuple(ngram_range),
        min_df=min_df,
        sublinear_tf=sublinear_tf,
        lowercase=True,
        stop_words=STOPWORDS_PT_BASICO,
    )
