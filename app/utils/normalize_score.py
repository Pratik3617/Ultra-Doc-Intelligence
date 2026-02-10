# normalize the FAISS score
def normalize_faiss_score(score: float) -> float:
    """
    Calibrated for OpenAI embedding L2 distances
    """
    if score <= 0.8:
        return 0.9
    elif score <= 1.0:
        return 0.75
    elif score <= 1.2:
        return 0.6
    elif score <= 1.5:
        return 0.4
    else:
        return 0.2
