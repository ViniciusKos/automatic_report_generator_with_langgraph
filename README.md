# Automatic Report Generator with LangGraph

## Overview
This project is an AI-powered business report generator that leverages natural language queries, DuckDB, and LangGraph workflow orchestration. It enables users to generate analytical reports and visualizations from retail data using simple English prompts. The system supports multiple queries, produces PDF reports, and is designed for extensibility and automation.

---

## Features
- **Natural Language Querying:** Users can request business insights using plain English (e.g., "Show me the total sales per month").
- **Automated SQL Generation:** Uses LLMs (OpenAI via LangChain) to translate user requests into SQL queries.
- **Data Extraction & Storage:** Downloads retail datasets (CSV, Excel, Parquet) and stores them in DuckDB, located in the `/db` folder.
- **Workflow Orchestration:** Utilizes LangGraph to manage multi-step report generation workflows.
- **Multi-Query PDF Reports:** Generates consolidated PDF reports for multiple queries, including tables and visualizations.
- **Extensible Functions:** Modular design for adding new data sources, report types, or visualizations.

---

## Folder Structure
```
automatic_report_generator_with_langgraph/
├── src/                # Source code
│   ├── config.py       # Configuration constants (URLs, filenames, DB names)
│   ├── extract_and_write_data.py  # Download and store retail data in DuckDB
│   ├── generate_business_report.py # Single-query report generation workflow
│   ├── generate_multiple_business_report.py # Multi-query PDF report generator
│   ├── workflow_functions.py      # Core workflow logic and utility functions
│   └── __pycache__/   # Python cache files
├── db/                # DuckDB database files
├── data/              # Raw and processed data files
├── reports/           # Generated PDF reports
│   └── Report_multiple_queries.pdf
├── README.md          # Project documentation
└── .env               # Environment variables (API keys, etc.)
```

---

## How It Works
1. **Data Acquisition:**
	- `extract_and_write_data.py` downloads retail data from a configurable URL and saves it to DuckDB in `/db`.
	- Supports CSV, Excel, and Parquet formats.

2. **Report Generation:**
	- `generate_business_report.py` orchestrates the workflow for a single query:
	  - Parses the user request.
	  - Generates SQL using an LLM.
	  - Executes the query on DuckDB.
	  - Produces a summary, table, and visualization.
	- `generate_multiple_business_report.py` processes multiple queries and compiles results into a single PDF report.

3. **Workflow Functions:**
	- `workflow_functions.py` contains reusable functions for parsing requests, executing SQL, generating visualizations, and assembling reports.

4. **Configuration:**
	- `config.py` centralizes URLs, filenames, and table/database names for easy modification.
	- `.env` stores sensitive information (e.g., OpenAI API key).

5. **Output:**
	- PDF reports are saved in `/reports`.
	- DuckDB database is stored in `/db`.

---

## Setup & Usage
1. **Install Dependencies:**
	```bash
	pip install -r requirements.txt
	```
2. **Configure Environment:**
	- Add your OpenAI API key and other settings to `.env`.
3. **Download Data:**
	```bash
	python src/extract_and_write_data.py --url <DATASET_URL>
	```
4. **Generate Reports:**
	- Single query:
	  ```bash
	  python src/generate_business_report.py --user_request "Show me the total sales per month"
	  ```
	- Multiple queries:
	  ```bash
	  python src/generate_multiple_business_report.py --user_request "Show me the total Quantity per country" "Show me the total sales per month"
	  ```
5. **Find Results:**
	- PDF reports in `/reports`
	- DuckDB database in `/db`

---

## Customization & Extensibility
- Add new data sources by updating `extract_and_write_data.py` and `config.py`.
- Extend report types or visualizations in `workflow_functions.py`.
- Modify workflow orchestration in `generate_business_report.py` and `generate_multiple_business_report.py`.

---

## Requirements
- Python 3.10+
- pandas, requests, tqdm, duckdb, reportlab, matplotlib, seaborn
- langchain, langgraph, python-dotenv

---

## License
See `LICENSE` for details.

---
## Acknowledgments
"This project was based on the original Scoras Academy Practical AI Projects repository."

"https://github.com/Scoras-Academy/Projetos_Praticos_de_IA/blob/main/Projetos_praticos_de_IA/Ferramenta%20de%20Gera%C3%A7%C3%A3o%20Automatica%20de%20Relat%C3%B3rios.ipynb"

---

## Authors
- Vinicius Kos

---

