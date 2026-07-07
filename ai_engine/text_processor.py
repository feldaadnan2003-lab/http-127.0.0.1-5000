"""Text cleaning, tokenization and keyword extraction utilities (NLP pre-processing)."""
import re
import string

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize


def ensure_nltk_data():
    """Download required NLTK corpora on first run (idempotent, quiet)."""
    resources = {
        "tokenizers/punkt": "punkt",
        "tokenizers/punkt_tab": "punkt_tab",
        "corpora/stopwords": "stopwords",
        "corpora/wordnet": "wordnet",
        "corpora/omw-1.4": "omw-1.4",
    }
    for path, package in resources.items():
        try:
            nltk.data.find(path)
        except LookupError:
            nltk.download(package, quiet=True)


ensure_nltk_data()

_LEMMATIZER = WordNetLemmatizer()
_STOPWORDS = set(stopwords.words("english"))
_STOPWORDS |= {"report", "ministry", "government", "please", "would", "could", "also"}


def clean_text(raw_text: str) -> str:
    """Lowercase, strip URLs/numbers/punctuation, collapse whitespace."""
    if not raw_text:
        return ""
    text = raw_text.lower()
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    text = re.sub(r"\d+", " ", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(clean: str) -> list:
    """Tokenize cleaned text and lemmatize, dropping stopwords and short tokens."""
    try:
        tokens = word_tokenize(clean)
    except LookupError:
        ensure_nltk_data()
        tokens = word_tokenize(clean)

    lemmatized = [
        _LEMMATIZER.lemmatize(tok)
        for tok in tokens
        if tok not in _STOPWORDS and len(tok) > 2
    ]
    return lemmatized


def preprocess(raw_text: str) -> str:
    """Full pipeline: clean -> tokenize -> lemmatize -> rejoin. Used for model input."""
    cleaned = clean_text(raw_text)
    tokens = tokenize(cleaned)
    return " ".join(tokens)


def extract_keywords(raw_text: str, vectorizer=None, top_n: int = 8) -> list:
    """Extract top keywords using TF-IDF weights from the trained vectorizer's vocabulary.

    Falls back to raw term-frequency ranking if no trained vectorizer is supplied.
    """
    processed = preprocess(raw_text)
    tokens = processed.split()
    if not tokens:
        return []

    if vectorizer is not None and hasattr(vectorizer, "vocabulary_"):
        idf_lookup = dict(zip(vectorizer.get_feature_names_out(), vectorizer.idf_))
        freq = {}
        for tok in tokens:
            freq[tok] = freq.get(tok, 0) + 1
        scored = {
            tok: count * idf_lookup.get(tok, 1.0)
            for tok, count in freq.items()
            if tok in idf_lookup
        }
        if scored:
            ranked = sorted(scored.items(), key=lambda kv: kv[1], reverse=True)
            return [word for word, _ in ranked[:top_n]]

    # Fallback: simple frequency ranking over the document itself
    freq = {}
    for tok in tokens:
        freq[tok] = freq.get(tok, 0) + 1
    ranked = sorted(freq.items(), key=lambda kv: kv[1], reverse=True)
    return [word for word, _ in ranked[:top_n]]
