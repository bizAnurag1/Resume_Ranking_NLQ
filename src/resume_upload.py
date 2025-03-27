from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
import io, os
from fastapi import UploadFile
from pdf2docx import Converter
from config import AZURE_STORAGE_CONNECTION_STRING, CONTAINER_NAME, STORAGE_ACCOUNT_NAME

# Initialize BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

def upload_to_adls(file):
    """Uploads a file to Azure Data Lake Storage (ADLS)."""
    blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=file.filename)
    
    # Upload file data
    blob_client.upload_blob(file.file, overwrite=True)

    return f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{CONTAINER_NAME}/{file.filename}"


