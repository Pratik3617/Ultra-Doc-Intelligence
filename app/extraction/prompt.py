from langchain_core.prompts import PromptTemplate

EXTRACTION_PROMPT = PromptTemplate(
    template="""
    You are an information extraction system for logistics documents.

    Extract the following fields ONLY if they are explicitly present in the document.
    If a field is missing, return null.

    Return STRICTLY valid JSON.
    Do not add explanations or extra text.

    Fields:
    - shipment_id
    - shipper
    - consignee
    - pickup_datetime
    - delivery_datetime
    - equipment_type
    - mode
    - rate
    - currency
    - weight
    - carrier_name

    Document:
    {context}
    """,
    input_variables=['context']
)