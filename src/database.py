from sqlalchemy import create_engine, Table, Column, Integer, Float, String, MetaData, JSON, NVARCHAR
import urllib, json
from config import AZURE_SQL_CONNECTION_STRING  # <- add these to config.py

class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(AZURE_SQL_CONNECTION_STRING)
        self.metadata = MetaData()

        self.resumes = Table(
            "resumes", self.metadata,
            Column("Id", Integer, primary_key=True, autoincrement=True),
            Column("Name", String(255)),
            Column("Email", String(255)),
            Column("Phone", String(50)),
            Column("City", String(100)),
            Column("Linkedin", String(255)),
            Column("Experience", Float),
            Column("Highest Education", String(255)),
            Column("Education Institute", String(500)),
            Column("Skills", JSON),
            Column("Soft Skills", JSON),
            Column("Profile", NVARCHAR(1000)),
            Column("Last Organization", JSON),
            Column("Second Last Organization", JSON),
            Column("Summary", NVARCHAR("max")),
            Column("Blob_URL", NVARCHAR(1000)),
        )

        self.metadata.create_all(self.engine)

    def insert_resume(self, resume_json, blob_url):
        data = json.loads(resume_json)
        data["Blob_URL"] = blob_url
        with self.engine.begin() as conn:
            conn.execute(self.resumes.insert(), data)
