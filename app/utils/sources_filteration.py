def filter_sources(sources, min_len=10):
    """
    Keep only meaningful source snippets
    """
    filtered = []
    for src in sources:
        snippet = src.get("snippet", "").strip()
        if len(snippet) >= min_len and not snippet.lower() in {"time"}:
            filtered.append(src)
    return filtered[:1]
