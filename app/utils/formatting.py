def format_docs(docs, include_source: bool = False):
    if include_source:
        return "\n\n".join(
            f"[Source: {doc.metadata.get('source', 'unknown')}]\n{doc.page_content}"
            for doc in docs
        )
    else:
        return "\n\n".join(
            doc.page_content for doc in docs
        )
