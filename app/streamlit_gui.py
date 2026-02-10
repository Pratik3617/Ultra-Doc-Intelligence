import streamlit as st
import requests
import os
from config import API_BASE_URL
from utils.source_content import trim_context, highlight_context


# Page config
st.set_page_config(
    page_title="Ultra Doc Intelligence",
    layout="wide"
)

st.title("Ultra Doc Intelligence")
st.caption("AI-powered document Q&A and structured extraction")

# Session State
if "session_id" not in st.session_state:
    st.session_state.session_id = None


# Upload Document
st.header("Upload Logistics Document")

uploaded_file = st.file_uploader(
    "Upload PDF, DOCX, or TXT",
    type=["pdf", "docx", "txt"]
)

if uploaded_file:
    with st.spinner("Uploading and indexing document..."):
        files = {
            "file": (uploaded_file.name, uploaded_file.getvalue())
        }

        response = requests.post(
            f"{API_BASE_URL}/upload",
            files=files
        )

        if response.status_code != 200:
            st.error(response.text)
        else:
            st.session_state.session_id = response.json()["session_id"]
            st.success("Document uploaded and indexed successfully!")


# Question Answering
st.header("Ask Questions")

question = st.text_input(
    "Ask a question about the document",
    disabled=st.session_state.session_id is None
)

if st.button("Ask", disabled=st.session_state.session_id is None):
    with st.spinner("Generating answer..."):
        payload = {
            "session_id": st.session_state.session_id,
            "question": question
        }

        response = requests.post(
            f"{API_BASE_URL}/ask",
            json=payload
        )

        if response.status_code != 200:
            st.error(response.text)
        else:
            data = response.json()

            # Answer
            st.subheader("Answer")
            st.write(data.get("answer", "No answer returned."))

            # Confidence
            st.subheader("Confidence")
            confidence = float(data.get("confidence", 0.0))
            st.progress(confidence)
            st.write(f"{confidence:.2f}")

            # Source Display
            st.subheader("Supporting Source")

            sources = data.get("sources", [])

            if not sources:
                st.info("No supporting source snippet found.")
            else:
                for src in sources:
                    source_name = os.path.basename(
                        src.get("source", "unknown")
                    )
                    page = src.get("page", "N/A")
                    raw_content = src.get("content", "")

                    trimmed = trim_context(raw_content)
                    highlighted = highlight_context(trimmed)

                    st.markdown(
                        f"""
                        **File:** `{source_name}`  
                        **Page:** `{page}`  

                        **Key Evidence:**  
                        > {highlighted}
                        """
                    )

                    with st.expander("View full source context"):
                        st.text(raw_content)


# Structured Extraction
st.header("Structured Extraction")

if st.button(
    "Run Structured Extraction",
    disabled=st.session_state.session_id is None
):
    with st.spinner("Extracting structured data..."):
        payload = {
            "session_id": st.session_state.session_id
        }

        response = requests.post(
            f"{API_BASE_URL}/extract",
            json=payload
        )

        if response.status_code != 200:
            st.error(response.text)
        else:
            st.subheader("Extracted Shipment Data")
            st.json(response.json())
