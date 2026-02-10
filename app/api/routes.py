import os
import tempfile
from typing import Dict

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

from app.ingestion.document_loader import Document_Loader
from app.extraction.extractor import ShipmentExtractor
from app.pipeline.rag_pipeline import build_rag_pipeline
from app.config import SUPPORTED_EXTENSIONS, CHUNK_SIZE, CHUNK_OVERLAP, LLM, EMBEDDING_MODEL, TEMPREATURE
from app.utils.sources_filteration import filter_sources_by_score

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate


router = APIRouter()

# In memory session store
SESSION: Dict[str, Dict] = {}

# Request models
class AskRequest(BaseModel):
    session_id : str
    question: str

class ExtractRequest(BaseModel):
    session_id: str

# Upload
@router.post("/upload")
def upload_document(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename)[1]

    if suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file.file.read())
        file_path = tmp.name

    # load document
    loader = Document_Loader(file_path)
    documents = loader.load()

    # chunking
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    chunks = splitter.split_documents(documents)

    # Vector store
    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL
    )
    vector_store = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings,
        distance_strategy="COSINE"
    )

    # prompt
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

    rag_chain = build_rag_pipeline(
        vector_store=vector_store,
        prompt=prompt,
        llm=llm
    )

    session_id = os.path.basename(file_path)

    SESSION[session_id] = {
        "rag_chain": rag_chain,
        "documents": documents
    }

    return {
        "session_id": session_id,
        "message": "Document uploaded and indexed successfully"
    }

# ask request
@router.post('/ask')
def ask_question(payload: AskRequest):
    if payload.session_id not in SESSION:
        raise HTTPException(status_code=404, detail="Invalid session_id")
    
    rag_chain = SESSION[payload.session_id]["rag_chain"]

    response = rag_chain.invoke(payload.question)

    clean_sources = filter_sources_by_score(
        response["sources"],
        threshold=0.6,
        top_k=1
    )

    return{
        "answer": response["answer"],
        "sources": clean_sources,
        "confidence": response["confidence"]
    }

# extract
@router.post("/extract")
def extract_structured_data(payload: ExtractRequest):
    if payload.session_id not in SESSION:
        raise HTTPException(status_code=404, detail="Invalid session_id")
    
    documents = SESSION[payload.session_id]["documents"]

    extractor = ShipmentExtractor(
        ChatOpenAI(model=LLM, temperature=TEMPREATURE)
    )

    extracted = extractor.extract(documents)

    return extracted