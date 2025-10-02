
import os
import argparse

import matplotlib
matplotlib.use('Agg')  # Use o backend Agg para evitar problemas com o display
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import io
import re
from reportlab.platypus import Image as ReportLabImage

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
from generate_business_report import generate_business_report

user_request = ["Show me the total Quantity per country", "Show me the total sales per month", "Which are the top 10 countries by sales?"]

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')

llm = ChatOpenAI(model_name="gpt-5-mini", temperature=0)



def generate_multi_query_report(queries, filename="Report_multiple_queries.pdf", title="Consolidated Analytical Report"):
    """
    Generates a PDF report containing multiple queries and their visualizations.
    
    Args:
        queries (list): List of strings with queries in natural language.
        filename (str): Name of the PDF file to be generated.
        title (str): Main title of the report.
    
    Returns:
        list: List of final states for each query.
    """
    # Create PDF document
    pdf_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reports')
    os.makedirs(pdf_folder, exist_ok=True)
    pdf_path = os.path.join(pdf_folder, filename)

    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Use existing styles
    title_style = styles['Title']
    title_style.alignment = 1  # Centered
    
    heading1_style = styles['Heading1']
    heading2_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # List of elements for the PDF
    elements = []
    
    # Add main title
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 0.5*inch))
    
    # List to store final states
    final_states = []
    
    # Process each query
    for i, query in enumerate(queries):
        print(f"Processing query {i+1}/{len(queries)}: {query}")
        
        # Generate report for this query
        state = generate_business_report(query)
        final_states.append(state)
        
        if state['errors']:
            print(f"Errors in query {i+1}:")
            for error in state['errors']:
                print(f"- {error}")
            continue
        
        # Add section title (query number)
        elements.append(Paragraph(f"Analysis {i+1}: {query}", heading1_style))
        elements.append(Spacer(1, 0.25*inch))
        
        # Process the report
        report_text = state['report']
        
        # Extract the executed SQL query
        sql_match = re.search(r'\*\*Executed SQL query:\*\*\n```sql\n(.*?)\n```', report_text, re.DOTALL)
        if sql_match:
            elements.append(Paragraph("<b>Executed SQL query:</b>", normal_style))
            sql_code = sql_match.group(1)
            elements.append(Paragraph(f"<font face='Courier'>{sql_code}</font>", normal_style))
            elements.append(Spacer(1, 0.1*inch))
        
        # Add data summary
        elements.append(Paragraph("Data Summary", heading2_style))
        
        # Extract summary items
        summary_section = re.search(r'## Data Summary\n\n(.*?)(?=\n\n##|\Z)', report_text, re.DOTALL)
        if summary_section:
            summary_items = re.findall(r'- (.*?)\n', summary_section.group(1))
            for item in summary_items:
                elements.append(Paragraph(f"• {item}", normal_style))
        
        elements.append(Spacer(1, 0.2*inch))
        
        # Add detailed data
        elements.append(Paragraph("Detailed Data", heading2_style))
        
        # Extract data table
        if state.get('query_result') is not None and not state['query_result'].empty:
            df = state['query_result'].head(10)
            
            # Create table
            table_data = [df.columns.tolist()]  # Header
            for i, row in df.iterrows():
                table_data.append([str(x) for x in row.tolist()])
            
            # Format the table
            table = Table(table_data, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            
            elements.append(table)
            
            if len(state['query_result']) > 10:
                elements.append(Paragraph(f"*Showing 10 of {len(state['query_result'])} records*", normal_style))
        
        # Add visualization created from raw data
        if state.get('query_result') is not None and not state['query_result'].empty:
            try:
                elements.append(Spacer(1, 0.3*inch))
                elements.append(Paragraph("Visualization", heading2_style))
                
                # Create a new figure
                plt.figure(figsize=(10, 6))
                
                # Determine chart type based on report
                df = state['query_result']
                
                # Limit to 10 items for better visualization
                if len(df) > 10:
                    df = df.head(10)
                
                # Determine columns for x and y
                if len(df.columns) >= 2:
                    x_col = df.columns[0]
                    y_col = df.columns[1]
                    
                    # Check if the request suggests a specific chart type
                    if "pizza" in query.lower() or "pie" in query.lower():
                        plt.figure(figsize=(8, 8))
                        plt.pie(df[y_col], labels=df[x_col], autopct='%1.1f%%')
                        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
                    elif "barra" in query.lower() or "bar" in query.lower():
                        plt.bar(df[x_col], df[y_col])
                        plt.xticks(rotation=45, ha='right')
                    else:
                        # Check if the data is numeric to decide chart type
                        if df[x_col].dtype.kind in 'ifc' and df[y_col].dtype.kind in 'ifc':
                            # Both are numeric, use scatter plot
                            plt.scatter(df[x_col], df[y_col])
                        else:
                            # Use bar chart as default
                            plt.bar(df[x_col], df[y_col])
                            plt.xticks(rotation=45, ha='right')
                    
                    plt.title(query)
                    plt.xlabel(x_col)
                    plt.ylabel(y_col)
                    plt.tight_layout()
                    
                    # Save the figure to a memory buffer
                    img_data = io.BytesIO()
                    plt.savefig(img_data, format='png', dpi=300)
                    img_data.seek(0)
                    
                    # Create an image for ReportLab
                    img = ReportLabImage(img_data, width=6*inch, height=4*inch)
                    elements.append(img)
                    
                    # Close the figure to free memory
                    plt.close()
                
            except Exception as e:
                print(f"Error creating visualization: {str(e)}")
                elements.append(Paragraph(f"Error adding visualization: {str(e)}", normal_style))
        
        # Add page break after each query (except the last)
        if i < len(queries) - 1:
            elements.append(PageBreak())
    
    # Build the PDF
    try:
        doc.build(elements)
        print(f"Multiple report saved as {filename}")
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
    
    return final_states


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate_business_report")
    parser.add_argument("--user_request", 
                        nargs="+", 
                        default=user_request, 
                        help="User request for the business report")
    args = parser.parse_args()
    generate_multi_query_report(args.user_request)