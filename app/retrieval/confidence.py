
from langchain_core.documents import Document
from app.utils.normalize_score import normalize_faiss_score
from typing import List, Tuple

def compute_confidence(
    scored_docs: List[Tuple[Document, float]], 
    k: int 
) -> float:
    """
    Compute a confidence score in [0, 1]
    FAISS score: lower = better
    """
    if not scored_docs:
        return 0.0
    
    best_score = scored_docs[0][1]

    # Normalize FAISS distance
    similarity_conf = normalize_faiss_score(best_score)

    # chunk agreement
    agreement_conf = len(scored_docs)/k

    confidence = 0.7 * similarity_conf + 0.3 * agreement_conf
    
    return round(confidence, 2)

