# Ultra Doc-Intelligence

## Overview

**Ultra Doc-Intelligence** is a proof-of-concept (POC) AI system that enables users to upload logistics documents (e.g., Bills of Lading, Rate Confirmations, Invoices) and interact with them using natural language questions.

The system uses **Retrieval-Augmented Generation (RAG)** to provide **grounded answers**, includes **hallucination guardrails**, returns a **confidence score** with each answer, and supports **structured data extraction** commonly required in Transportation Management Systems (TMS).

This project simulates an AI assistant embedded inside a logistics or freight management workflow.

---

## Key Features

*  Upload logistics documents (PDF, DOCX, TXT)
*  Ask natural language questions grounded in document content
*  Retrieval-Augmented Generation (RAG)
*  Hallucination guardrails
*  Confidence score per answer
*  Supporting source evidence
*  Structured shipment data extraction (JSON)
*  REST APIs + lightweight UI

---

## Architecture

```
┌────────────┐
│   UI       │  (Streamlit)
└─────┬──────┘
      │ REST
┌─────▼──────┐
│ FastAPI    │
│ Backend    │
└─────┬──────┘
      │
┌─────▼───────────────────────────────┐
│ Document Processing Pipeline         │
│ - Text Parsing                       │
│ - Chunking                           │
│ - Embeddings                         │
│ - Vector Store (FAISS)               │
└─────┬───────────────────────────────┘
      │
┌─────▼───────────┐
│ RAG Pipeline    │
│ - Retrieval     │
│ - Guardrails    │
│ - Confidence    │
└─────┬───────────┘
      │
┌─────▼───────────┐
│ LLM (OpenAI)    │
└─────────────────┘
```

---

## Document Upload & Processing

### Supported Formats

* PDF
* DOCX
* TXT

### Processing Steps

1. **Text Parsing** – Extract raw text from documents
2. **Chunking** – Split text into overlapping semantic chunks
3. **Embedding** – Generate vector embeddings using OpenAI models
4. **Indexing** – Store embeddings in a FAISS vector index (COSINE similarity)

---

## Chunking Strategy

* **Splitter:** RecursiveCharacterTextSplitter
* **Chunk Size:** 800 characters
* **Overlap:** 150 characters

### Rationale

* Preserves semantic continuity
* Improves recall for multi-line logistics fields
* Balances retrieval accuracy and context length

---

## Retrieval Method (RAG)

* **Vector Store:** FAISS
* **Similarity Metric:** Cosine similarity
* **Top-K Retrieval:** k = 4
* Retrieved chunks are passed as context to the LLM
* The LLM is instructed to answer **only using retrieved context**

---

## Guardrails Against Hallucination

The system includes multiple guardrails:

1. **Context-Only Answering**

   * The LLM prompt explicitly forbids answers outside retrieved context

2. **Missing Context Handling**

   * If relevant context is not retrieved, the system responds:

     > “Not found in document.”

3. **Similarity-Aware Retrieval**

   * Answers are grounded only when retrieval similarity is sufficient

4. **Source Transparency**

   * Supporting evidence is always returned with the answer

---

## Confidence Scoring

Each answer includes a **confidence score** between `0.0` and `1.0`.

### Confidence is derived from:

* Retrieval similarity scores
* Strength of top-K agreement
* Heuristic normalization

### Notes

* The confidence score is **heuristic**, not probabilistically calibrated
* It provides a useful signal for answer reliability
* Low confidence implies weak or missing document evidence

---

## Supporting Source Evidence

* Evidence is provided at the **chunk level**
* The UI displays a **trimmed, readable snippet**
* Full retrieved context is available via an expandable view
* This ensures transparency while maintaining usability

### Design Rationale

Chunk-level evidence is robust across noisy OCR and diverse document layouts.
Future improvements could refine evidence to sentence- or table-cell-level granularity.

---

## Structured Extraction

The system can extract structured shipment data from uploaded documents.

### Extracted Fields

```json
{
  "shipment_id": null,
  "shipper": null,
  "consignee": null,
  "pickup_datetime": null,
  "delivery_datetime": null,
  "equipment_type": null,
  "mode": null,
  "rate": null,
  "currency": null,
  "weight": null,
  "carrier_name": null
}
```

### Behavior

* Fields are extracted **only if explicitly present**
* Missing fields return `null`
* Output is **strict JSON**, suitable for downstream systems

---

## API Endpoints

### Upload Document

```
POST /upload
```

### Ask Question

```
POST /ask
```

**Returns**

* `answer`
* `sources`
* `confidence`

### Structured Extraction

```
POST /extract
```

---

## Minimal UI

A lightweight Streamlit UI allows reviewers to:

* Upload a document
* Ask natural language questions
* View answers, confidence scores, and source evidence
* Run structured extraction

UI design is intentionally minimal; usability and clarity are prioritized.

---

## Running Locally

### Prerequisites

* Python 3.10+
* OpenAI API key

### Setup

```bash
git clone <repo-url>
cd ultra-doc-intelligence
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file:

```env
OPENAI_API_KEY=your_api_key_here
```

### Run Backend

```bash
uvicorn app.main_api:app --reload
```

### Run UI

```bash
streamlit run app/streamlit_gui.py
```

---

## Hosted UI

A hosted UI can be deployed using platforms such as:

* Streamlit Community Cloud
* Hugging Face Spaces
* Render

The system is fully runnable locally and can be hosted with environment variable support for API keys.

---

## Failure Cases & Limitations

* OCR quality affects retrieval accuracy
* Confidence score is heuristic, not calibrated
* Single-document session scope
* Evidence granularity is chunk-level, not layout-aware
* No persistent storage (in-memory vector index)

---

## Future Improvements

* Layout-aware parsing for PDFs
* Multi-document reasoning
* Confidence calibration using answer verification
* User feedback loop for continuous improvement
* Persistent vector storage

---

## Summary

This project demonstrates a practical, end-to-end AI document intelligence system with strong grounding, guardrails, confidence scoring, and extraction capabilities — suitable as a foundation for real-world TMS AI assistants.

---
