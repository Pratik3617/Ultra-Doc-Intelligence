from typing import Dict, List
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser

from extraction.prompt import EXTRACTION_PROMPT
from utils.formatting import format_docs

class ShipmentExtractor:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.parser = JsonOutputParser()

    def extract(self, documents: List[Document]) -> Dict:
        """
        Extract structured shipment fields from full document context.
        Uses raw document text (no source annotations).
        """
        full_context = format_docs(documents, include_source=False)

        chain = (
            EXTRACTION_PROMPT | self.llm | self.parser
        )

        return chain.invoke({"context": full_context})
