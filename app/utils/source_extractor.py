from typing import List
import re


def extract_relevant_snippet(text: str, answer: str, max_lines: int = 2) -> str:
    """
    Extract minimal supporting lines from document text
    that justify the answer.
    """
    lines = text.splitlines()

    # find lines containing answer tokens
    answer_tokens = [tok for tok in re.findall(r"\w+", answer.lower()) if len(tok) > 2]

    matched_lines = []
    for line in lines:
        lower = line.lower()
        if any(tok in lower for tok in answer_tokens):
            matched_lines.append(line.strip())

        if len(matched_lines) >= max_lines:
            break

    # Fallback: return first non-empty line
    if not matched_lines:
        for line in lines:
            if line.strip():
                return line.strip()

    return " ".join(matched_lines)
