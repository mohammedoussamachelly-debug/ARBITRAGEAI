from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from vectorizer import get_embedding
import argparse

# Connect to Qdrant
client = QdrantClient(host="localhost", port=6333)

def search_products(query: str, collection: str, top_k: int = 5, category: str = None):
    vector = get_embedding(query)

    # Optional filter by category
    query_filter = None
    if category:
        query_filter = Filter(
            must=[
                FieldCondition(key="category", match=MatchValue(value=category))
            ]
        )

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
    parser.add_argument("--query", type=str, required=True, help="Search query")
    parser.add_argument("--collection", type=str, required=True, help="Qdrant collection name")
    parser.add_argument("--top_k", type=int, default=5, help="Number of results to return")
    parser.add_argument("--category", type=str, help="Optional category filter")

    args = parser.parse_args()
    search_products(args.query, args.collection, args.top_k, args.category)
