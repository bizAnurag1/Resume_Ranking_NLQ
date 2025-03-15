import streamlit as st
import requests

st.title("Resume Parsing & NLQ Bot")

# Upload multiple files (PDF and Word files supported)
st.subheader("Upload Resumes (PDF/DOCX Supported)")
uploaded_files = st.file_uploader("Choose resumes", type=["pdf", "docx"], accept_multiple_files=True)

if uploaded_files:
    files = [("files", (file.name, file.getvalue(), "application/octet-stream")) for file in uploaded_files]
    response = requests.post("http://127.0.0.1:8000/upload/", files=files)

    if response.status_code == 200:
        st.success("All resumes processed successfully!")
        st.json(response.json())  # Display processed resumes
    else:
        st.error(f"Error processing resumes: {response.text}")

# --- NLQ Chatbot UI ---
st.subheader("Ask Questions About Candidates")
query = st.text_input("Enter your query:", placeholder="E.g., Show candidates with more than 5 years of experience")

if st.button("Submit Query"):
    if query:
        response = requests.post("http://127.0.0.1:8000/query", json={"query": query})

        if response.status_code == 200:
            st.subheader("Query Response:")
            st.write(response.json())  # Display response
        else:
            st.error(f"Error fetching results: {response.text}")
    else:
        st.warning("Please enter a query before submitting.")
