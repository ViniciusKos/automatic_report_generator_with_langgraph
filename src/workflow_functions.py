import os
from langchain_core.prompts import ChatPromptTemplate
from typing import TypedDict, List, Dict, Any
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import duckdb
from config import DATABASE_NAME, TABLE_NAME


class State(TypedDict):
    user_request: str
    llm: Any
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
    f"""
    You are an assistant that creates SQL queries based on natural language requests.
    From the request below, generate a valid SQL query for the provided database.

    User request:
    {user_request}

    Available tables and their schemas:

    Table {TABLE_NAME}:
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
    
    response = state["llm"].invoke(prompt.format(user_request=user_request))
    sql_query = response.content.strip()
    
    # Clean markdown if present
    sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
    
    state['sql_query'] = sql_query
    return state



def connect_and_execute_sql_query(state: State) -> State:
    """
    Execute SQL query and store the result.
    """
    sql_query = state.get('sql_query', '')
    try:
        conn = duckdb.connect(database=f"{DATABASE_NAME}.duckdb")
        query_result = conn.execute(sql_query).df()
        state['query_result'] = query_result
        conn.close()
    except Exception as e:
        state['errors'].append(f"Error while executing SQL query: {e}")
    return state

def generate_visualization(state: State) -> State:
    """
    Generates visualizations based on the obtained data.
    """
    query_result = state.get('query_result')
    if query_result is None or query_result.empty:
        state['errors'].append("No data available to generate visualization.")
        return state
    
    try:
        plt.figure(figsize=(10, 6))
        numeric_cols = query_result.select_dtypes(include=['number']).columns.tolist()

        # Determine visualization type based on available columns
        if 'Description' in query_result.columns and any(col in query_result.columns for col in numeric_cols):
            # Bar chart for products
            value_col = next((col for col in numeric_cols if col in query_result.columns), None)
            if value_col:
                sns.barplot(data=query_result, x='Description', y=value_col)
                plt.title(f'{value_col.replace("_", " ").title()} by Description')
                plt.xlabel('description')
                plt.ylabel(value_col.replace("_", " ").title())
                plt.xticks(rotation=45)

        elif 'Country' in query_result.columns and any(col in query_result.columns for col in numeric_cols):
            # Bar chart for regions
            value_col = next((col for col in numeric_cols if col in query_result.columns), None)
            if value_col:
                sns.barplot(data=query_result, x='Country', y=value_col)
                plt.title(f'{value_col.replace("_", " ").title()} by Region')
                plt.xlabel('Country')
                plt.ylabel(value_col.replace("_", " ").title())

        elif 'InvoiceDate' in query_result.columns and any(col in query_result.columns for col in numeric_cols):
            # Line chart for time trend
            value_col = next((col for col in numeric_cols if col in query_result.columns), None)
            if value_col:
                plt.plot(query_result['InvoiceDate'], query_result[value_col])
                plt.title(f'Trend of {value_col.replace("_", " ").title()} Over Time')
                plt.xlabel('Date')
                plt.ylabel(value_col.replace("_", " ").title())
                plt.xticks(rotation=45)
        
        plt.tight_layout()
        state['visualization'] = plt.gcf()
        state['visualization'].savefig("visualization.png", dpi=300, bbox_inches="tight")
        
    except Exception as e:
        state['errors'].append(f"Error generating visualization: {str(e)}")
    
    return state


def generate_report(state: State) -> State:
    """
    Generates the final report based on the data and visualizations.
    """
    query_result = state.get('query_result')
    
    if query_result is None or query_result.empty:
        state['errors'].append("No data available to generate the report.")
        return state
    
    try:
        # Generate a summary of the data
        num_rows = len(query_result)

        report = f"# Report Generated Based on Request\n\n"
        report += f"**Original request:** {state['user_request']}\n\n"
        report += f"**Executed SQL query:**\n```sql\n{state['sql_query']}\n```\n\n"

        report += f"## Data Summary\n\n"
        report += f"- Total records: {num_rows}\n"

        # Add specific statistics based on available columns
        if 'total_quantity' in query_result.columns:
            total_quantity = query_result['total_quantity'].sum()
            avg_quantity = query_result['total_quantity'].mean()
            report += f"- Total quantity: {total_quantity:.2f}\n"
            report += f"- Average quantity: {avg_quantity:.2f}\n"

        if 'Description' in query_result.columns and query_result['Description'].nunique() < 10:
            report += f"- Included descriptions: {', '.join(query_result['Description'].unique())}\n"

        if 'Country' in query_result.columns and query_result['Country'].nunique() < 10:
            report += f"- Included countries: {', '.join(query_result['Country'].unique())}\n"

        # Add data table
        report += f"\n## Detailed Data\n\n"

        # Limit to 10 rows to avoid overloading the report
        sample_data = query_result.head(10)
        report += sample_data.to_markdown() + "\n"

        if len(query_result) > 10:
            report += f"\n*Showing 10 of {len(query_result)} records*\n"

        state['report'] = report
    except Exception as e:
        state['errors'].append(f"Error generating report: {str(e)}")

    return state
