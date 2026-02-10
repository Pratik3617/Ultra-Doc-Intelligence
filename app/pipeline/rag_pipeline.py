from langchain_core.runnables import RunnableParallel, RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from app.retrieval.retriever import ConfidenceAwareRetriever

def build_rag_pipeline(vector_store, prompt, llm):
    retriever = ConfidenceAwareRetriever(vector_store, k=4)
    parser = StrOutputParser()

    rag_chain = (
        {
            "retrieval": RunnableLambda(retriever.retrieve),
            "question": RunnablePassthrough()
        }
        | RunnableLambda(
            lambda x: {
                "question": x["question"],
                "context": x["retrieval"]["context"],
                "sources": x["retrieval"]["sources"],
                "confidence": x["retrieval"]["confidence"]
            }
        )
        | RunnableParallel({
            "answer": prompt | llm | parser,
            "sources": lambda x: x["sources"],
            "confidence": lambda x: x["confidence"]
        })
    )

    return rag_chain