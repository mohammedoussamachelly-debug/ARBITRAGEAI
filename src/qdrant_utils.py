import os
import uuid
from pathlib import Path
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

# Load .env file - search from current directory up
load_dotenv()

def get_client():
    qdrant_host = os.getenv("QDRANT_HOST")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")

    # Host can be defaulted for convenience, but API key should never be hardcoded.
    if not qdrant_host:
        qdrant_host = "https://dfd0b68f-16b0-481c-93f7-0efd4d2b121b.us-east4-0.gcp.cloud.qdrant.io"

    if not qdrant_api_key:
        raise RuntimeError(
            "Missing QDRANT_API_KEY. Set it in your environment or a local .env file (not committed)."
        )

    print(f"DEBUG: Qdrant host={qdrant_host}")

    return QdrantClient(url=qdrant_host, api_key=qdrant_api_key, https=True)

def create_collection(client, collection_name: str, vector_size: int):
    if not client.collection_exists(collection_name=collection_name):
        client.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
        )

def upload_batch(client, collection_name: str, vectors: list[list[float]], payloads: list[dict]):
    points = [
        PointStruct(id=str(uuid.uuid4()), vector=vec, payload=payload)
        for vec, payload in zip(vectors, payloads)
    ]
    client.upsert(collection_name=collection_name, points=points)
