from typing import Dict, List, Tuple
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

from app.utils.formatting import format_docs
from app.retrieval.confidence import compute_confidence
from app.utils.sentence_evidence import select_best_sentence


class ConfidenceAwareRetriever:
    def __init__(self, vector_store: FAISS, k: int = 4):
        self.vector_store = vector_store
        self.k = k

    def retrieve(self, question: str) -> Dict[str, object]:

        scored_docs: List[Tuple[Document, float]] = (
            self.vector_store.similarity_search_with_score(
                question, k=self.k
            )
        )

        if not scored_docs:
            return {
                "context": "Not found in document",
                "sources": [],
                "confidence": 0.0
            }

        # Chunk-level context for LLM 
        docs = [doc for doc, _ in scored_docs]
        context = format_docs(docs, include_source=False)

        # Confidence
        confidence = float(compute_confidence(scored_docs, self.k))

        # Sentence-level evidence
        question_embedding = self.vector_store.embeddings.embed_query(question)

        sources = []
        for doc, score in scored_docs:
            best_sentence = select_best_sentence(
                doc.page_content,
                question_embedding,
                self.vector_store.embeddings
            )

            sources.append({
                "source": doc.metadata.get("source"),
                "page": doc.metadata.get("page"),
                # sentence-level evidence (fallback to chunk if needed)
                "content": best_sentence or doc.page_content,
                "score": float(score)
            })

        return {
            "context": context,
            "sources": sources,
            "confidence": confidence
        }
