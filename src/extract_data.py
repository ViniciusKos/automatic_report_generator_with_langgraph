import pandas as pd
import requests
from io import BytesIO
from tqdm import tqdm
import argparse
import os
from config import URL, FILE_NAME

def download_online_retail_data(url: str = None, saved_file_name: str = None ) -> None:
    # add progress bar
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
    df = pd.read_excel(bio)

    # Ensure the CSV is saved in the parent 'data' folder
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(parent_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    # Use only the base name of the file
    base_name = os.path.basename(saved_file_name)
    save_path = os.path.join(data_dir, base_name)
    return df.to_csv(save_path)

def main():
    parser = argparse.ArgumentParser(description="Download online retail dataset")
    parser.add_argument("--url", default=URL, help="Dataset URL")
    parser.add_argument("--saved_file_name", default=FILE_NAME, help="File name to be written with format e.g: data.csv")
    args = parser.parse_args()

    download_online_retail_data(url = args.url, 
                                saved_file_name = args.saved_file_name)


if __name__ == "__main__":
    main()