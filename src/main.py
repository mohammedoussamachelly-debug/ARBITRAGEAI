import os
import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm
from vectorize import get_embeddings
from qdrant_utils import get_client, create_collection, upload_batch
from payload_utils import normalize_payload

load_dotenv(dotenv_path=r'C:\Users\MSI\Desktop\ArbitrageAI\.env')

CHUNK_SIZE = 100
VECTOR_SIZE = 384  # for all-MiniLM-L6-v2

def load_dataset(path: str, rename_map: dict) -> pd.DataFrame:
    df = pd.read_parquet(path) if path.endswith(".parquet") else pd.read_csv(path)
    df = df.rename(columns=rename_map)
    df = df[["name", "description", "price", "category"]].dropna()
    return df

def process_and_upload(client, df: pd.DataFrame, collection: str):
    print(f"\n[INFO] Creating collection: {collection}")
    create_collection(client, collection, VECTOR_SIZE)
    for i in tqdm(range(0, len(df), CHUNK_SIZE)):
        chunk = df.iloc[i:i+CHUNK_SIZE]
        texts = (chunk["name"] + " " + chunk["description"]).tolist()
        print(f"[INFO] Processing chunk {i//CHUNK_SIZE+1} / {((len(df)-1)//CHUNK_SIZE)+1}")
        vectors = get_embeddings(texts)
        # Normalize payloads and add AR model URLs
        payloads = [normalize_payload(row) for _, row in chunk.iterrows()]
        upload_batch(client, collection, vectors, payloads)
        print(f"[INFO] Uploaded chunk {i//CHUNK_SIZE+1}")

if __name__ == "__main__":
    client = get_client()
    
    # Delete old collections to start fresh
    try:
        client.delete_collection(collection_name="clothing")
        print("Deleted old clothing collection")
    except:
        pass
    
    try:
        client.delete_collection(collection_name="watches")
        print("Deleted old watches collection")
    except:
        pass
    
    try:
        client.delete_collection(collection_name="nike_shoes")
        print("Deleted old nike_shoes collection")
    except:
        pass
    
    datasets = {
        "clothing": {
            "path": "data/clothing.parquet",
            "rename_map": {"title": "name", "subtitle": "description", "price": "price", "category": "category"}
        },
        "watches": {
            "path": "data/watches.csv",
            "rename_map": {"name": "name", "description": "description", "price": "price", "category": "category"}
        },
        "nike_shoes": {
            "path": "data/nike_shoes.csv",
            "rename_map": {"name": "name", "description": "description", "price": "price", "category": "category"}
        }
    }

    for collection, config in datasets.items():
        df = load_dataset(config["path"], config["rename_map"])
        process_and_upload(client, df, collection)
