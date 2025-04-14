from fastapi import FastAPI, UploadFile, File
import shutil, os, logging
from pydantic import BaseModel
from config import RESUME_FOLDER
from src.resume_upload import upload_to_adls
from src.extractor import ResumeExtractor
from src.azure_openai import AzureOpenai
from src.database import DatabaseManager
from src.nlq import NLQProcessor
from typing import List
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  #frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

class QueryRequest(BaseModel):
    query: str

# Ensure the resume folder exists
os.makedirs(RESUME_FOLDER, exist_ok=True)

@app.post("/upload/")
async def upload_resumes(files: List[UploadFile] = File(...)):
    extractor = ResumeExtractor()
    openai_processor = AzureOpenai()
    db_manager = DatabaseManager()

    processed_resumes = []

    for file in files:
        # file_path = os.path.join(RESUME_FOLDER, file.filename)
        
        # with open(file_path, "wb") as buffer:
        #     shutil.copyfileobj(file.file, buffer)
        logging.getLogger("azure").setLevel(logging.CRITICAL)

        file_path = upload_to_adls(file)

        # Extract text using Azure Document Intelligence
        extracted_text = extractor.extract_text(file_path)

        # Convert extracted text to structured JSON using Azure OpenAI
        resume_json = openai_processor.convert_to_json(extracted_text)
        # print("data extracted successfully!!")
        # print(resume_json)
        # Store JSON data in SQL Server
        db_manager.insert_resume(resume_json, file_path)
        # print("data insertion completed")
        processed_resumes.append({"filename": file.filename, "status": "Processed"})

    # return {"message": "Batch processing complete", "processed_resumes": processed_resumes}
    return True


@app.post("/query")
async def answer_query(query: QueryRequest):
    nlq = NLQProcessor()

    response = nlq.ask_database(query)
    return response

# Example Queries
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8001)