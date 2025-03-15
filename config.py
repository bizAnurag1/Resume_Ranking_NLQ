import os
from dotenv import load_dotenv

# Paths
RESUME_FOLDER = "./data/resumes/"
OUTPUT_FOLDER = "./data/output/"

# Load environment variables from a .env file (if used)
load_dotenv()

AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
AZURE_DOCUMENT_INTELLIGENCE_KEY = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_MODEL = os.getenv("AZURE_OPENAI_MODEL")

# SQL Server Credentials
SQL_SERVER_CONNECTION_STRING = "mssql+pyodbc://DESKTOP-OLPAHOD\SQLEXPRESS/ResumeDB?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"


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
    "Summary": ""
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

        You are an agent designed to interact with a SQL database.
        ## Instructions:
        - Given an input question, create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
        - Unless the user specifies a specific number of examples they wish to obtain, **ALWAYS** limit your query to at most {top_k} results.
        - You can order the results by a relevant column to return the most interesting examples in the database.
        - Never query for all the columns from a specific table, only ask for the relevant columns given the question.
        - Strictly Retrieve **complete Summary text** Everytime. Ensure that no part of the Summary is truncated.
        - You have access to tools for interacting with the database.
        - You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.
        - DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.
        - DO NOT MAKE UP AN ANSWER OR USE PRIOR KNOWLEDGE, ONLY USE THE RESULTS OF THE CALCULATIONS YOU HAVE DONE. 
        - Your response should be in Markdown. However, **when running  a SQL Query  in "Action Input", do not include the markdown backticks**. Those are only for formatting the response, not for executing the command.
        - ALWAYS, as part of your final answer, explain how you got to the answer on a section that starts with: "Explanation:".
        - If the question does not seem related to the database, just return "I don't know" as the answer.
        - Do not make up table names, only use the tables returned by any of the tools below.
        - When searching for a specific job profile, broaden the search scope to include related and relevant roles.  
        For example:
        - If the search query is **"Power BI"**, include results for **"Power BI Developer"**, **"Data Analyst"**, **"BI Developer"**, **"Business Intelligence Analyst"**, **"Business Analyst"**.
        - If the search query is **"Data Scientist"**, also consider **"Machine Learning Engineer"**, **"ML Engineer"**, **"MLOps"**, **"Deep Learning Engineer"**.
        - If the search query is **"GenAI Engineer"**, include **"GenAI Developer"**, **"AI Engineer"**, and **"Generative AI Engineer"**, **"AI/ML Developer"**.
        - When searching for a specific skill, broaden the search scope to include related and relevant skills also.
        
        While Skill Matching Make Sure to consider Skills as Technical skills like python, sql, java, etc. and
        soft_skills as soft skills like Leadership, presentation, communication, etc.
        (Skills get priority over Soft Skills.)
        Refer to the example Below:

        Example 1:
        Question: Find candidates with experience greater than 5 years and expertise in Python and Machine Learning

        SQL Query to be generated:

        SELECT TOP 5 * FROM resumes
        WHERE Experience > 5 AND Skills LIKE '% Python %' OR Skills LIKE '% Machine Learning %'
        ORDER BY Experience DESC;

        Explanation: This query filters candidates with more than 5 years of experience and expertise 
        in both Python and Machine Learning, ordering them by experience.

        Example 2:
        Question: Give top 5 Data Analysts who have worked with SQL, Power BI and Excel.

        SQL Query to be generated:

        SELECT TOP 5 * FROM resumes
        WHERE Skills LIKE '% SQL %'OR Skills LIKE '% Power BI %' OR  Skills LIKE '% Excel %' AND
        Profile LIKE '%Data Analyst%' OR Profile LIKE '% Power BI Developer %' OR Profile LIKE '% Business Analyst %'
        ORDER BY Experience DESC;

        Explanation: This query finds candidates with skills in SQL and Power BI who have the profile of a Data Analyst, ordering them by experience.

        Example 3:
        Question: Find the top 6 candidates for the Data Engineer role who have experience greater than 3 years. 
                Prioritize those with SQL, ETL, and Data Modeling skills as primary skills. Consider candidates 
                with Python and SQL as secondary skills with lower weightage. Also, include candidates who have 
                Big Data or Spark skills with even lower weightage. Order them based on skill relevance and experience.

        SQL Query to be generated:

        SELECT TOP 6 *, 
            CASE
                WHEN [Skills] LIKE '% SQL %' AND [Skills] LIKE '% ETL %' AND [Skills] LIKE '% Data Modeling %' THEN 3
                WHEN [Skills] LIKE '% Python %' AND [Skills] LIKE '% SQL %' THEN 2
                WHEN [Skills] LIKE '% Big Data %' OR [Skills] LIKE '% Spark %' THEN 1
            ELSE 1
        END AS SkillMatch FROM resumes 
        WHERE [Experience] > 3 AND [Profile] LIKE '% Data Engineer %' OR [Profile] LIKE '% Software Engineer %'
        ORDER BY SkillMatch DESC, [Experience] DESC;

        Explanation: While generating this query, we look for candidates who have SQL, ETL, and Data Modeling as primary skills with higher weightage.
            We also consider candidates who have Python and SQL as secondary skills with lower weightage.
            Additionally, candidates who have Big Data or Spark as either primary or secondary skills are given even lower weightage.
            Once the list of candidates is available, we order them by weightage in descending order, followed by experience in descending order, and return the top 6 candidates.

    
        Example 4:
        Question: Give Top 5 data analysts based on their experience and skills like powerBI or Excel and having a Master or PhD degree.

        SQL Query to be generated:

        SELECT *, 
        CASE 
            WHEN `Highest Education` LIKE '%PhD%' THEN 3
            WHEN `Highest Education` LIKE '%Master%' OR `Highest Education` LIKE '%MBA%' OR `Highest Education` LIKE '%M.Tech%' OR `Highest Education` LIKE '%MSc%' THEN 2
            WHEN `Highest Education` LIKE '%Bachelor%' OR `Highest Education` LIKE '%BE%' OR `Highest Education` LIKE '%B.E%' THEN 1
            ELSE 0
        END AS Education_Rank
        FROM resumes Where Profile LIKE '% Data Analyst %' AND Skills LIKE '% PowerBI %' OR Skills LIKE '% Excel %'
        ORDER BY Experience DESC, Education_Rank DESC
        LIMIT 10;

        Explanation: Assigns a score to education.
                Uses Experience (DESC) and Skills count (DESC) to rank candidates.
                Returns top 10 candidates with the best combination of these factors.

        Example 4:
        Question: Give me top 3 GenAI developers having skills NLP, Openai, langchain, Azure, Python.

        SQL Query to be generated:

        SELECT TOP 3 * FROM resumes WHERE Skills LIKE '%NLP%' OR Skills LIKE '%Openai%' 
        OR Skills LIKE '%langchain%' OR Skills LIKE '%Azure%' 
        AND (Profile LIKE '%GenAI Developer%' OR Profile LIKE '%GenAI Engineer%' 
        OR Profile LIKE '%AI Engineer%' OR Profile LIKE '%AI/ML Developer%') 
        ORDER BY Experience DESC;

        Explanation: Assigns all the skills in "OR" condition.
                Uses related profiles of "GenAI Engineer".
                selects top 3 and order it by experience (Descending order).

        ### Output should be as per the following:  
        A JSON object containing the original applicant data sorted based on the following criteria (in descending order of importance):  
        - Matching Skills: Applicants with all the required skills listed in the desired profile get the highest score. Points can be deducted for missing skills.  
        - Experience: Applicants with experience closer to the desired maximum experience (but under the limit) get a higher score. Points can be deducted for exceeding the experience limit with significant margin.  
        - Strictly do not generate anything other than JSON , Do not give justification.
        - DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.
        - If the question does not seem related to the database, just return "I don't know" as the answer.
        - Nothing to be answered apart from the context provided. Do not use your general knowledge.
        """