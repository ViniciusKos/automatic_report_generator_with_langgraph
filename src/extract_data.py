import pandas as pd
import requests
from io import BytesIO
from tqdm import tqdm
import argparse
import duckdb
import os
from config import URL, FILE_NAME, DATABASE_NAME, TABLE_NAME

def download_online_retail_data(url: str = None) -> pd.DataFrame:
    """
    Download retail data from a URL and return as a DataFrame.
    
    Args:
        url (str): The URL to download the data from.
    Returns:
        pd.DataFrame: The loaded retail data.
    """
    resp = requests.get(url, stream=True)
    resp.raise_for_status()
    total = int(resp.headers.get("content-length", 0))

    chunk_size = 1024
    bio = BytesIO()
    with tqdm(total=total, unit="B", unit_scale=True, desc="downloading...") as pbar:
        for chunk in resp.iter_content(chunk_size=chunk_size):
            bio.write(chunk)
            pbar.update(len(chunk))

    # go back to the buffer start
    bio.seek(0)
    if url.endswith(".xlsx") or url.endswith(".xls"):
        df = pd.read_excel(bio)
    elif url.endswith(".csv"):
        df = pd.read_csv(bio)
    elif url.endswith(".parquet"):
        df = pd.read_parquet(bio)
    else:
        raise ValueError("Unsupported file format. Supported formats: .csv, .xlsx, .xls, .parquet")
    return df

def save_as_duckdb_table(df: pd.DataFrame, 
                         database_name:str = DATABASE_NAME,
                         table_name: str = TABLE_NAME) -> : None
    """
    Save a DataFrame as a DuckDB table.
    
    Args:
        df (pd.DataFrame): Data to save.
        database_name (str): Name of the DuckDB database (without extension).
        table_name (str): Name of the table to create.
    Returns:
        duckdb.DuckDBPyConnection: Connection to the DuckDB database.
    """
    conn = duckdb.connect(database=f"{database_name}.duckdb")
    conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM df")
    conn.close()

    return None



def main():
    """
    Main entry point: parses arguments, downloads data, saves to DuckDB.
    
    Inputs: command-line arguments --url and --saved_file_name
    Outputs: Prints confirmation and creates DuckDB table from downloaded data
    """
    parser = argparse.ArgumentParser(description="Download online retail dataset")
    parser.add_argument("--url", default=URL, help="Dataset URL")
    parser.add_argument("--saved_file_name", default=FILE_NAME, help="File name to be written with format e.g: data.csv")
    args = parser.parse_args()

    df = download_online_retail_data(url = args.url, 
                                saved_file_name = args.saved_file_name)
    
    save_as_duckdb_table(df, table_name="sales_data")
    print("DuckDB in-memory database created with table 'sales_data'")

if __name__ == "__main__":
    main()