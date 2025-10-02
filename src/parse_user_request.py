import os
from dotenv import load_dotenv
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from typing import TypedDict, List, Dict, Any
import pandas as pd


load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')

llm = ChatOpenAI(model_name="gpt-5o", temperature=0)

class State(TypedDict):
    user_request: str
    sql_query: str
    query_result: pd.DataFrame
    report: str
    visualization: Any
    errors: List[str]


def parse_user_request(state: State) -> State:
    """
    Converts the user's request into an SQL query.
    """
    user_request = state['user_request']
    
    prompt = ChatPromptTemplate.from_template(
    """
    You are an assistant that creates SQL queries based on natural language requests.
    From the request below, generate a valid SQL query for the provided database.

    User request:
    {user_request}

    Available tables and their schemas:

    Tabela 'retail_data':
    - InvoiceNo (VARCHAR)
    - StockCode (VARCHAR)
    - Description (VARCHAR)
    - Quantity (INTEGER)
    - InvoiceDate (TIMESTAMP)
    - UnitPrice (FLOAT)
    - CustomerID (FLOAT)
    - Country (VARCHAR)

    Importante:
    - Use only the tables and columns provided.
    - Make sure the query is compatible with DuckDB.
    - Return only the pure SQL query, without markdown markers or decorations.
    - Do not use ``` or sql in your response.
    """
    )
    
    response = llm.invoke(prompt.format(user_request=user_request))
    sql_query = response.content.strip()
    
    # Limpar marcadores markdown se ainda estiverem presentes
    sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
    
    state['sql_query'] = sql_query
    return state