import streamlit as st
import requests, json
import time, pandas as pd

# Streamlit Page Configuration
st.set_page_config(page_title="Resume Parser & NLQ Bot", layout="wide")

# Custom CSS for better styling
st.markdown(
    """
    <style>
        .sidebar .sidebar-content {
            background-color: #f8f9fa;
        }
        .stTextInput>div>div>input {
            border-radius: 10px;
        }
        .stButton>button {
            width: 100%;
            border-radius: 10px;
            background-color: #007bff;
            color: white;
        }
        .stChatMessage {
            background-color: #e9ecef;
            padding: 10px;
            border-radius: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ---- SIDEBAR SECTION (For Resume Uploads) ----
with st.sidebar:
    st.title("📂 Resume Upload")
    st.subheader("Upload Resumes (PDF/DOCX)")
    
    uploaded_files = st.file_uploader(
        "Choose resumes",
        type=["pdf", "docx"],
        accept_multiple_files=True
    )

    if uploaded_files:
        if st.button("Upload & Process"):
            with st.spinner("Processing resumes... ⏳"):
                files = [
                    ("files", (file.name, file.getvalue(), "application/octet-stream"))
                    for file in uploaded_files
                ]
                response = requests.post("http://127.0.0.1:8001/upload/", files=files)

                if response.status_code == 200:
                    st.success("✅ All resumes processed successfully!")
                    # st.json(response.json())  # Display processed resumes
                else:
                    st.error(f"❌ Error processing resumes: {response.text}")

# ---- MAIN SECTION (Chat Interface for NLQ) ----
st.title("Resume Ranking Intelligent Bot")
st.subheader("Ask about candidate details")

chat_history = st.session_state.get("chat_history", [])

query = st.text_input(
    "Enter your query:", 
    placeholder="E.g., Show candidates with more than 5 years of experience"
)

if st.button("Submit Query"):
    if query:
        with st.spinner("Fetching response... ⏳"):
            response = requests.post("http://127.0.0.1:8001/query", json={"query": query})

            if response.status_code == 200:
                try:
                    data_str = response.json()
                    data = json.loads(data_str)

                    if isinstance(data, list):
                        # Convert lists inside dictionaries to comma-separated strings
                        formatted_data = [
                            {k: ", ".join(v) if isinstance(v, list) else v for k, v in item.items()} 
                            for item in data
                        ]

                        df = pd.DataFrame(formatted_data)
                        df.insert(0, "Ranking", range(1, len(df) + 1))
                    elif isinstance(data, dict):
                        # Convert lists inside the dictionary to comma-separated strings
                        formatted_data = {k: ", ".join(v) if isinstance(v, list) else v for k, v in data.items()}

                        # Convert to DataFrame (single-row DataFrame)
                        df = pd.DataFrame([formatted_data])
                        df.insert(0, "Ranking", range(1, len(df) + 1))
                    else:
                        df = pd.DataFrame()
                    # st.dataframe(df, hide_index=True, column_config={"Resume Text": None, "Id": None, "SkillMatch": None})
                    st.data_editor(df, column_config={"Summary": st.column_config.TextColumn(width="large"), 
                                                      "Resume Text": None, "Id": None, "SkillMatch": None, "Blob_URL": st.column_config.LinkColumn(
                                                      "Resume",  # Column Name
                                                      display_text="View"),
                                                      }, hide_index=True)
                    # st.table(df)

 
                except Exception as e:
                    st.error(f"⚠️ Error processing response: {str(e)}")
    else:
        st.warning("⚠️ Please enter a query before submitting.")

# Display Chat History (like ChatGPT)
# st.subheader("Chat History")
# for role, message in chat_history:
#     with st.chat_message("assistant" if role == "Bot" else "user"):
#         st.write(f"**{role}:** {message}")
