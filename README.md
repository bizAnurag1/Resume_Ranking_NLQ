## Resume Ranking using NLQ
##### Overview
This project enables resume ranking using Natural Language Queries (NLQ). It allows users to upload resumes, extract structured information, and rank candidates based on job requirements.

##### Key Features
✅ Upload multiple resumes
✅ Extract candidate details using Azure Document Intelligence
✅ Store data in Azure SQL Database
✅ Query resumes using NLQ (Natural Language Queries)
✅ Rank candidates based on job requirements

##### Workflow
1️⃣ Upload resumes (PDF, DOCX, etc.)
2️⃣ Extract metadata (Name, Skills, Experience, Education, etc.)
3️⃣ Store structured data in Azure SQL Database
4️⃣ Use NLQ to search and rank candidates
5️⃣ Display results in a user-friendly interface

##### Technology Stack
🔹 Azure OpenAI GPT-4o – Converts extracted text to structured data
🔹 Azure Document Intelligence – Extracts resume details
🔹 Azure Blob Storage – Stores uploaded resumes
🔹 Azure SQL Database – Stores structured resume data
🔹 NLQ Processing – Enables natural language-based search

##### Use Case Example
User Query: "Find top 5 candidates skilled in Python with 5+ years of experience."
System Response: Ranked list of candidates matching the criteria.

##### Future Enhancements
✅ Improved AI-based ranking based on job descriptions
✅ Integration with HR systems for automated hiring
