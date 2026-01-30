import os
import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm
from vectorizer import get_embeddings
from qdrant_utils import client, create_collection, upload_batch

load_dotenv()

CHUNK_SIZE = 100
VECTOR_SIZE = 384  # for all-MiniLM-L6-v2

def load_dataset(path: str, rename_map: dict) -> pd.DataFrame:
    df = pd.read_parquet(path) if path.endswith(".parquet") else pd.read_csv(path)
    df = df.rename(columns=rename_map)
    df = df[["name", "description", "price", "category"]].dropna()
    return df

def process_and_upload(df: pd.DataFrame, collection: str):
    create_collection(collection, VECTOR_SIZE)
    for i in tqdm(range(0, len(df), CHUNK_SIZE)):
        chunk = df.iloc[i:i+CHUNK_SIZE]
        texts = (chunk["name"] + " " + chunk["description"]).tolist()
        vectors = get_embeddings(texts)
        payloads = chunk.to_dict(orient="records")
        upload_batch(collection, vectors, payloads)

if __name__ == "__main__":
    datasets = {
        "clothing": {
            "path": "data/clothing.parquet",
            "rename_map": {"title": "name", "subtitle": "description", "price": "price", "category": "category"}
        },
        "watches": {
            "path": "data/watches.csv",
            "rename_map": {"name": "name", "description": "description", "price": "price", "category": "category"}
        }
    }

    for collection, config in datasets.items():
        df = load_dataset(config["path"], config["rename_map"])
        process_and_upload(df, collection)
