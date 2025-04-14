from sqlalchemy import create_engine, Table, Column, Integer, Float, String, MetaData, JSON, NVARCHAR, text
from azure.identity import DefaultAzureCredential
import urllib, json
import pyodbc, struct
from config import server, driver, database

class DatabaseManager:
    def __init__(self):

        # Get token using DefaultAzureCredential (works with managed identity)
        credential = DefaultAzureCredential()
        token = credential.get_token("https://database.windows.net/").token
        access_token = bytes(token, "utf-8")
        token_struct = struct.pack("B", len(access_token)) + access_token

        # Build ODBC connection string
        conn_str = (
            f"DRIVER={driver};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"Encrypt=yes;"
            f"TrustServerCertificate=no;"
            f"Connection Timeout=30;"
        )
        params = urllib.parse.quote_plus(conn_str)
        AZURE_SQL_CONNECTION_STRING = f"mssql+pyodbc:///?odbc_connect={params}"

        # self.engine = create_engine(AZURE_SQL_CONNECTION_STRING)
        # Create engine with token-based authentication
        self.engine = create_engine(
            AZURE_SQL_CONNECTION_STRING,
            connect_args={"attrs_before": {1256: token_struct}},
            fast_executemany=True,
        )
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
            # conn.commit()