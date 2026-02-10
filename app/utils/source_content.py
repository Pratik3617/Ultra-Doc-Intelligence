# utilities for extracting relevant source content

def trim_context(text: str, max_chars: int = 280) -> str:
    """Trim long OCR context for display"""
    if not text:
        return "No supporting context available."
    text = text.strip()
    return text if len(text) <= max_chars else text[:max_chars] + "..."


def highlight_context(text: str) -> str:
    """Light highlighting of common logistics keywords"""
    highlights = [
        "lbs", "kg",
        "Delivery Date",
        "Pickup",
        "Drop",
        "Cherry Avenue",
        "Fontana",
        "FTL",
        "Container"
    ]
    for h in highlights:
        text = text.replace(h, f"**{h}**")
    return text