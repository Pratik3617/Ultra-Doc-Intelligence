import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import re

NOISE_PATTERNS = [
    r"page \d+ of \d+",
    r"powered by",
    r"demo",
    r"copyright",
    r"all rights reserved"
]

def is_noise_sentence(sentence: str) -> bool:
    s = sentence.lower()
    if len(s) < 30:
        return True
    for pattern in NOISE_PATTERNS:
        if re.search(pattern, s):
            return True
    return False

def split_sentences(text: str):
    """
    OCR-tolerant sentence splitter
    """
    return [
        s.strip()
        for s in re.split(r"(?<=[.!?])\s+", text)
        if len(s.strip()) > 20
    ]


def select_best_sentence(
    chunk_text: str,
    question_embedding: np.ndarray,
    embedder
):
    sentences = split_sentences(chunk_text)

    # Filter out boilerplate / footer / header sentences
    sentences = [
        s for s in sentences
        if not is_noise_sentence(s)
    ]

    if not sentences:
        return None

    sentence_embeddings = embedder.embed_documents(sentences)

    scores = cosine_similarity(
        [question_embedding],
        sentence_embeddings
    )[0]

    best_idx = max(
        range(len(sentences)),
        key=lambda i: (scores[i], len(sentences[i]))
    )

    return sentences[best_idx]
