def filter_sources_by_score(sources, threshold=0.6, top_k=1):
    """
    sources: List[dict] with 'score' key
    """
    if not sources:
        return []

    # Keep sources under threshold (lower = better for cosine)
    good_sources = [
        src for src in sources
        if src.get("score") is not None and src["score"] <= threshold
    ]

    # Fallback: take best scored source
    if not good_sources:
        good_sources = sorted(
            sources, key=lambda x: x.get("score", 1.0)
        )

    return good_sources[:top_k]
