import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from vectorize import get_embedding
import argparse

# Load environment variables
load_dotenv()

def get_client():
    qdrant_host = os.getenv("QDRANT_HOST", "https://dfd0b68f-16b0-481c-93f7-0efd4d2b121b.us-east4-0.gcp.cloud.qdrant.io")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    if not qdrant_api_key:
        raise RuntimeError("Missing QDRANT_API_KEY. Set it in your environment or a local .env file.")
    return QdrantClient(url=qdrant_host, api_key=qdrant_api_key, https=True)

# Connect to Qdrant
client = get_client()

def search_products(query: str, collection: str, top_k: int = 5, category: str = None):
    from qdrant_client.models import PointStruct
    vector = get_embedding(query)

    # Optional filter by category
    query_filter = None
    if category:
        query_filter = Filter(
            must=[
                FieldCondition(key="category", match=MatchValue(value=category))
            ]
        )

    try:
        # Try newer API
        results = client.search(
            collection_name=collection,
            query_vector=vector,
            limit=top_k,
            query_filter=query_filter
        )
    except AttributeError:
        # Fallback to older API
        results = client.query_points(
            collection_name=collection,
            query=vector,
            limit=top_k,
            query_filter=query_filter
        ).points

    print(f"\n🔎 Top {top_k} results for: '{query}' in '{collection}'\n")
    for i, hit in enumerate(results, 1):
        payload = hit.payload
        name = payload.get('name', payload.get('title', 'N/A'))
        price = payload.get('price', 0)
        category_val = payload.get('category', 'N/A')
        description = payload.get('description', payload.get('subtitle', 'N/A'))
        print(f"{i}. {name} — ${price:.2f} [{category_val}]")
        print(f"   {description}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", type=str, required=True, help="Search query")
    parser.add_argument("--collection", type=str, required=True, help="Qdrant collection name")
    parser.add_argument("--top_k", type=int, default=5, help="Number of results to return")
    parser.add_argument("--category", type=str, help="Optional category filter")

    args = parser.parse_args()
    search_products(args.query, args.collection, args.top_k, args.category)
