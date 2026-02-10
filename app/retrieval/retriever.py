from typing import Dict, List, Tuple
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

from app.utils.formatting import format_docs
from app.retrieval.confidence import compute_confidence


class ConfidenceAwareRetriever:
    def __init__(self, vector_store: FAISS, k: int = 4):
        self.vector_store = vector_store
        self.k = k

    def retrieve(self, question: str):

        scored_docs = self.vector_store.similarity_search_with_score(
            question, k=self.k
        )

        if not scored_docs:
            return {
                "context": "Not found in document",
                "sources": [],
                "confidence": 0.0
            }

        docs = [doc for doc, _ in scored_docs]

        context = format_docs(docs, include_source=False)

        confidence = float(compute_confidence(scored_docs, self.k))

        sources = [
            {
                "source": doc.metadata.get("source"),
                "page": doc.metadata.get("page"),
                "content": doc.page_content,
                "score": float(score)   # ✅ cast here
            }
            for doc, score in scored_docs
        ]

        return {
            "context": context,
            "sources": sources,
            "confidence": confidence
        }
