from dotenv import load_dotenv
from ingestion.document_loader import Document_Loader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import PromptTemplate

from pipeline.rag_pipeline import build_rag_pipeline
from extraction.extractor import ShipmentExtractor
from config import LLM, EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP, TEMPREATURE
from utils.sources_filteration import filter_sources

load_dotenv()


def main():
    # Load document
    loader = Document_Loader(
        "/home/prateek/Ultra_Doc_Intelligence/app/data/BOL53657_billoflading.pdf"
    )
    documents = loader.load()

    # Chunking
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    chunks = splitter.split_documents(documents)

    # Embeddings + Vector Store
    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL
    )

    vector_store = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings,
        distance_strategy="COSINE"
    )

    # Prompt (RAG)
    prompt = PromptTemplate(
        template="""
        You are a helpful assistant.

        Answer the question using ONLY the information in the provided context.
        If the answer is not explicitly present, respond with:
        "Not found in document."

        Question:
        {question}

        Context:
        {context}
        """,
        input_variables=["question", "context"]
    )

    # LLM
    llm = ChatOpenAI(
        model=LLM,
        temperature=TEMPREATURE
    )

    # Build RAG pipeline
    rag_chain = build_rag_pipeline(
        vector_store=vector_store,
        prompt=prompt,
        llm=llm
    )

    # Ask Question (Q&A)
    qa_response = rag_chain.invoke("Who is the consignee?")

    print("\n--- Question Answering ---")
    print("Answer:", qa_response["answer"])
    print("Sources:", filter_sources(qa_response["sources"]))
    print("Confidence:", qa_response["confidence"])
    
    # Structured Extraction
    extractor = ShipmentExtractor(llm)

    extracted_data = extractor.extract(documents)

    print("\n--- Structured Extraction ---")
    print(extracted_data)


if __name__ == "__main__":
    main()

