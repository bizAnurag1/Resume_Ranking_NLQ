from sqlalchemy import create_engine, Table, Column, Integer, Float, String, MetaData, JSON, NVARCHAR
from config import SQL_SERVER_CONNECTION_STRING, AZURE_SQL_CONNECTION_STRING
import json, pyodbc

class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(AZURE_SQL_CONNECTION_STRING)
        self.metadata = MetaData()

        self.resumes = Table(
            "resumes", self.metadata,
            Column("Id", Integer, primary_key=True, autoincrement=True),
            Column("Name", String(255)),  # Applicant Full Name
            Column("Email", String(255)),  # Email of Applicant
            Column("Phone", String(50)),  # Contact Number of Applicant
            Column("City", String(100)),  # Extracted City from Address or Contact Details
            Column("Linkedin", String(255)),  # LinkedIn Profile URL
            Column("Experience", Float),  # Professional Experience in Years
            Column("Highest Education", String(255)),  # Highest Degree Obtained
            Column("Education Institute", String(500)),  # Educational Institute
            Column("Skills", JSON),  # Key Technical Skills (Array Format)
            Column("Soft Skills", JSON),  # Key Soft Skills (Array Format)
            Column("Profile", NVARCHAR(1000)),  # Job Profile Based on Skills & Experience
            Column("Last Organization", JSON),  # Work Experience Details 
            Column("Second Last Organization", JSON),  # Work Experience Details 
            Column("Summary", NVARCHAR("max")),  # 4-5 Line Summary of the Resume
            Column("Blob_URL", NVARCHAR(1000)), # resume path
            # Column("Resume Text", NVARCHAR("max")) # Full Extracted Resume Text from PDF
        )

        self.metadata.create_all(self.engine)

    def insert_resume(self, resume_json, blob_url):
        data = json.loads(resume_json)
        data["Blob_URL"] = blob_url
        with self.engine.begin() as conn:
            conn.execute(self.resumes.insert(), data)
            conn.commit()