json_content = """{
    "Name": "",
    "Email": "",
    "Phone": "",
    "City": "",
    "Linkedin": "",
    "Experience": "",
    "Highest Education": "",
    "Education Institute": "",
    "Skills": ["", "", "..."],
    "Soft Skills": ["", "", "..."],
    "Profile": "",
    "Last Organization": ["", "", ""],
    "Second Last Organization": ["", "", ""],
    "Summary": "",
    "Resume Text": ""
}"""


PROMPT_TEMPLATE = f"""You are an AI Assistant who helps extract with Named entity Recognition from the Resumes provided. You will extract the following from the resume:

        'Name': (Give Applicant's Full Name) Extract the full name of the applicant from the resume text. Change it to Camel case. ex: Vishal Patil
        'Email': (Give Email of the Applicant if Provided) Extract only if an email is mentioned.
        'Phone': (Give Contact Number of the Applicant if Provided) Extract only if a phone number is explicitly mentioned.
        'City': (Extract City from Address or Contact Details if Mentioned) If the city is explicitly mentioned in the address, provide it; otherwise, extract from other available details.
        'Linkedin': (Extract LinkedIn Profile URL if Mentioned) Extract the LinkedIn profile link if present.
        'Experience': (Extract Professional Experience in Years if Mentioned.)
                    If Experience not mentioned in Resume text Then Calculate using previous work durations.
                    if you got "Current" or "Present" in Duration then consider it as "March 2025" and Calculate the Experience accordingly.
                    Do not add any symbols before and after the float value.
        'Highest Education': (Extract the Highest Education Qualification Mentioned) Provide the highest degree obtained by the candidate.
        'Education Institute': (Extract the Institute Name of the Highest Education Qualification) Provide the name of the institute where the highest degree was obtained.
        'Skills': (Extract all Technical Skills Mentioned in Resume) Example: Python, SQL, Azure, ML, etc. Present the skills in an array format.
        'Soft Skills': (Extract all Soft Skills Mentioned in Resume) Example: Leadership, Presentation, Communication, etc. Present the skills in an array format.
        'Profile': (Extract Job Profile Based on Skills & Experience) Determine the candidate's job profile based on the listed skills and experience.  
                Example: Software Engineer, UI Developer, Business Analyst, etc.  
                Do not include the level of seniority and extra description related to the profile (e.g., Junior, Senior).
        'Last Organization': (Extract the last Organization Name, Duration, and Profile of candiate in that organization). Present the details in an array format.
                Example: ["Bizmetric Ltd.", "Jan 2020 - Dec 2024", "Data Scientist"]. 
        'Second Last Organization': (Extract the Second last Organization Name, Duration, and Profile of candiate in that organization). Present the details in an array format.
                Example: ["Infosys", "Jan 2018 - Dec 2020", "Data Engineer"].
        'Summary': (Provide a 4-5 Line Summary of the Resume in texual format). Summarize the applicant’s key qualifications, experience, and skills concisely.
        'Resume Text': (Add the provided Full Resume Text in texual format).

        After Extracting the above Named Entity Recognition fields and fill the provided JSON template. 
        Ensure all keys in the template are present in the output, even if the value is empty or unknown. 
        If a specific piece of information is not found in the text, use 'Not provided' as the value.

        JSON template:
        {json_content}

        Instructions:
        1. Carefully analyse the resume text.
        2. Extract relevant information for each field in the JSON template.
        3. If a piece of information is not explicitly stated, make a reasonable inference based on the context.
        4. Ensure all keys from the template are present in the output JSON.
        5. Format the output as a valid JSON string.
        6. Output the filled JSON template only, without any additional text or explanations.
        7. Do not include any additional text, explanations, or comments."""


MSSQL_AGENT_PREFIX = """
        ##########################
        Don't evaluate the database and table schema for each execution, instead use the schema mentioned below:
        You should access 'resumes' table to answer the queries. Following is the schema of the table:

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
        Column("Last Organization", JSON),  # Work Experience Details (Array format)
        Column("Second Last Organization", JSON),  # Work Experience Details (Array format)
        Column("Summary", NVARCHAR(max)),  # 4-5 Line Summary of the Resume
        Column("Resume Text", NVARCHAR(max)) # Full Extracted Resume Text from PDF"""