from typing import Dict, List, Tuple
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

from utils.formatting import format_docs
from retrieval.confidence import compute_confidence
from utils.source_extractor import extract_relevant_snippet

class ConfidenceAwareRetriever:
    def __init__(self, vector_store: FAISS, k: int=4):
        self.vector_store = vector_store
        self.k = k

    def retrieve(self, question: str)-> Dict[str, object]:

        scored_docs: List[Tuple[Document, float]] = (
            self.vector_store.similarity_search_with_score(
                question, 
                k=self.k
            )
        )

        if not scored_docs:
            return {
                "context": "Not found in document",
                "sources": [],
                "confidence": 0.0
            }
        
        docs = [doc for doc,_ in scored_docs]
        confidence = compute_confidence(scored_docs, self.k)

        return {
            'context': format_docs(docs, include_source=False),
            "sources": [
                {
                    "source": doc.metadata.get("source", "unknown"),
                    "page": doc.metadata.get("page"),
                    "snippet": extract_relevant_snippet(
                        doc.page_content,
                        question
                    )
                }
                for doc in docs
            ],
            "confidence": confidence
        }