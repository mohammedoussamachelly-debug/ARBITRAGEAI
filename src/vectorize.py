import argparse
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, Range, MatchValue
from vectorizer import get_embedding

load_dotenv()

QDRANT_HOST = os.getenv("QDRANT_HOST")
QDRANT_PORT = int(os.getenv("QDRANT_PORT"))
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

client = QdrantClient(
    url=QDRANT_HOST,
    port=QDRANT_PORT,
    api_key=QDRANT_API_KEY,
    https=True
)

def build_filter(category=None, min_price=None, max_price=None):
    conditions = []
    if category:
        conditions.append(FieldCondition(key="category", match=MatchValue(value=category)))
    if min_price is not None or max_price is not None:
        price_range = {}
        if min_price is not None:
            price_range["gte"] = float(min_price)
        if max_price is not None:
            price_range["lte"] = float(max_price)
        conditions.append(FieldCondition(key="price", range=Range(**price_range)))
    return Filter(must=conditions) if conditions else None

def search_products(query: str, collection: str, top_k: int = 5, category: str = None, min_price=None, max_price=None):
    vector = get_embedding(query)
    query_filter = build_filter(category, min_price, max_price)

    results = client.search(
        collection_name=collection,
        query_vector=vector,
        limit=top_k,
        query_filter=query_filter
    )

    print(f"\n🔎 Top {top_k} results for: '{query}' in '{collection}'\n")
    for i, hit in enumerate(results, 1):
        payload = hit.payload
        print(f"{i}. {payload['name']} — ${payload['price']:.2f} [{payload['category']}]")
        print(f"   {payload['description']}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", type=str, required=True)
    parser.add_argument("--collection", type=str, required=True)
    parser.add_argument("--top_k", type=int, default=5)
    parser.add_argument("--category", type=str)
    parser.add_argument("--min_price", type=float)
    parser.add_argument("--max_price", type=float)

    args = parser.parse_args()
    search_products(
        query=args.query,
        collection=args.collection,
        top_k=args.top_k,
        category=args.category,
        min_price=args.min_price,
        max_price=args.max_price
    )
