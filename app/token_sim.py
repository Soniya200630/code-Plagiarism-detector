"""Step 2 - lexical (token) similarity: TF-IDF over token n-grams + cosine."""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .preprocess import normalize_tokens

N_GRAMS = (3, 4, 5)


def _analyzer(code: str):
    toks = normalize_tokens(code)
    grams = []
    for n in N_GRAMS:
        grams += [" ".join(toks[i:i + n]) for i in range(len(toks) - n + 1)]
    return grams or list(toks)  # very short files: fall back to single tokens


def token_sim(a: str, b: str) -> float:
    ta, tb = normalize_tokens(a), normalize_tokens(b)
    if not ta or not tb:
        return 0.0
    if ta == tb:
        return 1.0
    try:
        vec = TfidfVectorizer(analyzer=_analyzer)
        m = vec.fit_transform([a, b])
        return float(cosine_similarity(m[0], m[1])[0, 0])
    except ValueError:  # empty vocabulary
        return 0.0
