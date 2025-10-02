
import os
import argparse

import pandas as pd
from dotenv import load_dotenv
from langchain_openai.chat_models import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from workflow_functions import (
    parse_user_request,
    connect_and_execute_sql_query,
    generate_visualization,
    generate_report,
    State
)

user_request = "Show me the total Quantity per country"

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')

llm = ChatOpenAI(model_name="gpt-5-mini", temperature=0)



def generate_business_report(user_request: str) -> State:
    """
    Generate a business report based on a user request.
    
    Args:
        user_request (str): The user's natural language request.
    Returns:
        State: The final state containing the report and other details.
    """

    workflow = StateGraph(State)
    workflow.add_node("parse_user_request", parse_user_request)
    workflow.add_node("connect_and_execute_sql_query", connect_and_execute_sql_query)
    workflow.add_node("generate_visualization", generate_visualization)
    workflow.add_node("generate_report", generate_report)

    workflow.add_edge(START, "parse_user_request")
    workflow.add_edge("parse_user_request", "connect_and_execute_sql_query")
    workflow.add_edge("connect_and_execute_sql_query", "generate_visualization")
    workflow.add_edge("generate_visualization", "generate_report")
    workflow.add_edge("generate_report", END)

    app = workflow.compile()

    initial_state: State = {
        "user_request": user_request,
        "llm": llm,
        "sql_query": "",
        "query_result": pd.DataFrame(),
        "report": "",
        "visualization": None,
        "errors": []
    }

    final_state = app.invoke(initial_state)
    print(f"Errors processing the request {user_request}: {final_state['errors']}")
    return final_state


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate_business_report")
    parser.add_argument("--user_request", default=user_request, help="User request for the business report")
    args = parser.parse_args()
    generate_business_report(args.user_request)