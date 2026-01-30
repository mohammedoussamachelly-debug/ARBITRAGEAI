# ArbitrageAI

A project for arbitrage analysis using AI and vector search with Qdrant.

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Set up Qdrant (cloud or local).
3. Add credentials to `.env`.
4. Run `python src/main.py` to load data.
5. Run `python src/retrieve.py --query "your query" --collection "collection_name"` to search.

## Files

- `src/main.py`: Data ingestion
- `src/retrieve.py`: Search interface
- `src/vectorize.py`: Embedding utilities
- `src/qdrant_utils.py`: Qdrant helpers
- `notebook/demo.ipynb`: Demo notebook

## Roadmap

- [ ] Add web interface
- [ ] Support more data sources
- [ ] Improve search accuracy