from fastapi import FastAPI, UploadFile, File
import shutil
import os
from pydantic import BaseModel
from config import RESUME_FOLDER
from src.extractor import ResumeExtractor
from src.azure_openai import AzureOpenAI
from src.database import DatabaseManager
from src.nlq import NLQProcessor
from typing import List

app = FastAPI()

class QueryRequest(BaseModel):
    query: str

# Ensure the resume folder exists
os.makedirs(RESUME_FOLDER, exist_ok=True)

@app.post("/upload/")
async def upload_resumes(files: List[UploadFile] = File(...)):
    extractor = ResumeExtractor()
    openai_processor = AzureOpenAI()
    db_manager = DatabaseManager()

    processed_resumes = []

    for file in files:
        file_path = os.path.join(RESUME_FOLDER, file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract text using Azure Document Intelligence
        extracted_text = extractor.extract_text(file_path)

        # Convert extracted text to structured JSON using Azure OpenAI
        resume_json = openai_processor.convert_to_json(extracted_text)

        # Store JSON data in SQL Server
        db_manager.insert_resume(resume_json)

        processed_resumes.append({"filename": file.filename, "status": "Processed"})

    return {"message": "Batch processing complete", "processed_resumes": processed_resumes}


@app.post("/query")
async def answer_query(query: QueryRequest):
    nlq = NLQProcessor()

    response = nlq.ask_database(query)
    return response

# Example Queries
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)