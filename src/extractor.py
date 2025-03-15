from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from config import AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT, AZURE_DOCUMENT_INTELLIGENCE_KEY

class ResumeExtractor:
    def __init__(self):
        # Initialize Document Intelligence Client
        self.document_intelligence_client = DocumentIntelligenceClient(
            AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT, AzureKeyCredential(AZURE_DOCUMENT_INTELLIGENCE_KEY)
        )

    def extract_text(self, file_path: str):
        """Extract text from PDF using Azure AI Document Intelligence."""
        try:
            with open(file_path, "rb") as f:
                poller = self.document_intelligence_client.begin_analyze_document("prebuilt-read", body=f)
            result = poller.result()
            return result.content  # Extracted text
        except Exception as e:
            raise RuntimeError(f"Azure Document Intelligence Error: {str(e)}")
