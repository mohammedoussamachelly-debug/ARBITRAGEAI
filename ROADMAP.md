# ROADMAP.md

## ArbitrageAI: Strategic Development Roadmap

---

### Completed Milestones

- Set up Qdrant vector database and connected it to the embedding pipeline  
- Implemented semantic search using SentenceTransformers (MiniLM)  
- Built CLI interface for product retrieval with filtering by price and category  
- Designed and tested product ingestion pipeline from CSV/JSON  
- Embedded and indexed sample datasets (e.g., sneakers) into Qdrant  
- Added ROI and liquidity metadata to product payloads  
- Developed `vectorize.py` for batch embedding and indexing  
- Created `main.py` as the application entry point  
- Structured project into modular components (retrieval, embedding, UI, ingestion)

---

### In Progress

- **Real-time payload injection from resale market APIs (eBay, StockX, GOAT)**  
  - Automatically update ROI, price, and liquidity from external sources  

- **Batch ingestion of multi-domain product datasets**  
  - Load large product sets (e.g., sneakers, watches, furniture) from CSV/JSON  
  - Normalize schema and push to Qdrant  

- **Streamlit UI prototype**  
  - Semantic search bar, filters, and product card rendering  

- **AR-based real-life visualization module**  
  - Integration with ARKit (iOS) and ARCore (Android)  
  - Support for `.glb` and `.usdz` 3D model overlays  

- **Expansion of retrieval logic**  
  - Multi-product queries  
  - Investment-aware ranking  

---

### Next Steps 

- Add `--investment_mode` flag to rank by ROI + liquidity  
- Enable filtering by `roi`, `liquidity`, and `volatility` in `qdrant_utils.py`  
- Compute composite investment score using weighted formula (e.g., `0.6 * ROI + 0.3 * liquidity - 0.1 * volatility`)  
- Finalize Streamlit UI with product cards and filters  

- **Enable real-life product viewing with AR**  
  - Trigger AR view from product cards  
  - Preview products in physical space (e.g., shoes on feet, watches on wrist)  

- **Enable image-based product search**  
  - Integrate visual encoder (e.g., CLIP) to extract image embeddings  
  - Allow users to upload a product photo and retrieve visually similar items  
  - Store image embeddings in Qdrant alongside text and financial metadata  
  - Support hybrid queries: “Find products like this image, but cheaper and with high ROI”  

- **Investment Intelligence (AI Model 🧠)**  
  - Train a lightweight regression model to predict future resale value  
  - Use historical pricing, brand trends, and product metadata as features  
  - Optionally classify products as “good” vs “bad” investments using a classifier (e.g., XGBoost)  
  - Integrate model predictions into ranking logic for smarter recommendations  
  - Personalize investment picks based on user behavior and portfolio goals  
