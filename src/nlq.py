from langchain_openai import AzureChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain.prompts import BasePromptTemplate
from sqlalchemy import create_engine
from config import AZURE_OPENAI_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_MODEL
from config import SQL_SERVER_CONNECTION_STRING, MSSQL_AGENT_PREFIX, AZURE_SQL_CONNECTION_STRING
from langchain_community.agent_toolkits import create_sql_agent, SQLDatabaseToolkit
import json, pandas as pd
from fastapi.responses import JSONResponse


class NLQProcessor():
    def __init__(self):
        """Initialize NLQ Processor with Azure OpenAI and SQL Database connection."""
        
        # Create the database connection
        self.engine = create_engine(AZURE_SQL_CONNECTION_STRING)
        self.db = SQLDatabase(self.engine)

        # Initialize Azure OpenAI Model
        self.llm = AzureChatOpenAI(
            api_key=AZURE_OPENAI_KEY,
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            openai_api_version="2024-02-01",  # Ensure this matches your Azure API version
            model="gpt-4o",
            deployment_name=AZURE_OPENAI_MODEL,
            temperature=0
        ) 

        # Define the NLQ Prompt Template
        # self.prompt_template = PromptTemplate(
        #     input_variables=["question", "dialect", "table_info"],
        #     template="""
        #     Given the database schema:
        #     {table_info}
        #     Translate the following natural language query into a SQL query:
        #     {question}
        #     Use {dialect} SQL dialect.
        #     """
        # )

        toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)

        # Create an agent for NLQ processing
        self.agent_executor = create_sql_agent(prefix=MSSQL_AGENT_PREFIX,
                llm=self.llm,
                toolkit=toolkit,
                top_k=10,
                agent_type="openai-tools",
                verbose=True,
                agent_executor_kwargs= {"return_intermediate_steps": False}
            )

    def ask_database(self, nlq: str):
        """Executes an NLQ query and returns the result."""
        try:
            print("analyzing..")
            response = self.agent_executor.invoke(nlq)
            # if isinstance(response, bytes):  
            #     response = response.decode("utf-8")  # Convert bytes to string if needed
            # print(response)
            json_res = response.get("output").strip("```json").strip("\n```")
            # json_response = json.loads(json_res)
            print(json_res)
            # df = pd.DataFrame(json_response)
            return JSONResponse(content=json_res)
        except Exception as e:
            return {"error": str(e)}

