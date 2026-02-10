from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from app.config import SUPPORTED_EXTENSIONS


class Document_Loader:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)

        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if self.file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type: {self.file_path.suffix}. "
                f"Supported types: {SUPPORTED_EXTENSIONS}"
            )

    def load(self) -> List[Document]:
        """
        Load document and return LangChain Document objects.
        """
        suffix = self.file_path.suffix.lower()

        if suffix == ".pdf":
            loader = PyPDFLoader(str(self.file_path))
            docs = loader.load()

            # Guardrail: detect scanned / empty PDFs
            if not any(doc.page_content.strip() for doc in docs):
                raise ValueError(
                    "PDF appears to be scanned or contains no extractable text. "
                    "OCR is not enabled in this POC."
                )

            return docs

        elif suffix == ".docx":
            loader = Docx2txtLoader(str(self.file_path))
            return loader.load()

        elif suffix == ".txt":
            loader = TextLoader(str(self.file_path), encoding="utf-8")
            return loader.load()

        else:
            # Should never hit due to earlier check
            raise RuntimeError("Unhandled file type")
