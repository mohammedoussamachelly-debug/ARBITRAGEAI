import streamlit as st
import sys
sys.path.append('src')

from qdrant_utils import get_client
from qdrant_client.models import Filter, FieldCondition, MatchValue
import pandas as pd
from streamlit.components.v1 import html
from payload_utils import normalize_payload

# Page Configuration
st.set_page_config(
    page_title="ArbitrageAI - Smart Product Search & AR",
    page_icon="👟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Beautiful UI
st.markdown("""
    <style>
        :root {
            --text: #0b0b0b;
            --muted: #6b7280;
            --border: #111111;
            --bg: #ffffff;
        }

        .stApp {
            background: #ffffff;
        }
        
        .main-header {
            font-size: 2rem;
            font-weight: 800;
            color: #0b0b0b;
            margin-bottom: 0.25rem;
            letter-spacing: -0.02em;
        }
        
        .subheader {
            color: #6b7280;
            font-size: 0.95rem;
            margin-bottom: 1.5rem;
        }
        
        .product-card {
            border-radius: 12px;
            padding: 1.25rem;
            background: #ffffff;
            border: 1px solid #111111;
            transition: all 0.2s ease;
            margin-bottom: 1rem;
        }
        
        .product-card:hover {
            box-shadow: 0 6px 18px rgba(0, 0, 0, 0.06);
        }
        
        .product-name {
            font-size: 1.1rem;
            font-weight: 700;
            color: #0b0b0b;
            margin-bottom: 0.35rem;
        }
        
        .product-meta {
            display: flex;
            gap: 1rem;
            margin: 0.6rem 0;
            font-size: 0.85rem;
        }
        
        .price-tag {
            font-size: 1.2rem;
            font-weight: 800;
            color: #0b0b0b;
        }
        
        .category-badge {
            display: inline-block;
            padding: 0.2rem 0.65rem;
            background-color: #f3f4f6;
            color: #111111;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            border: 1px solid #111111;
        }
        
        .ar-ready-badge {
            display: inline-block;
            padding: 0.4rem 0.75rem;
            background-color: #f3f4f6;
            color: #111111;
            border-radius: 6px;
            font-weight: 600;
            margin-top: 0.5rem;
            border: 1px solid #111111;
        }
        
        .footer {
            text-align: center;
            padding: 2rem;
            color: #6b7280;
            font-size: 0.85rem;
            border-top: 1px solid #111111;
            margin-top: 3rem;
        }

        .assistant-card {
            border-radius: 12px;
            padding: 0.75rem;
            background: #ffffff;
            border: 1px solid #111111;
            color: #0b0b0b;
        }

        .assistant-hint {
            font-size: 0.8rem;
            color: #6b7280;
            margin-bottom: 0.6rem;
        }

        .chat-bubble-user {
            background: #f3f4f6;
            padding: 0.45rem 0.6rem;
            border-radius: 10px;
            margin-bottom: 0.45rem;
            color: #0b0b0b;
            font-size: 0.85rem;
            border: 1px solid #111111;
        }

        .chat-bubble-assistant {
            background: #ffffff;
            padding: 0.45rem 0.6rem;
            border-radius: 10px;
            margin-bottom: 0.6rem;
            color: #0b0b0b;
            font-size: 0.85rem;
            border: 1px solid #111111;
        }

        .product-row {
            display: flex;
            gap: 0.75rem;
            overflow-x: auto;
            padding-bottom: 0.25rem;
        }

        .product-tile {
            border-radius: 10px;
            padding: 0.9rem;
            background: #ffffff;
            border: 1px solid #111111;
            min-width: 260px;
            flex: 0 0 auto;
        }

        .assistant-card.floating {
            position: sticky;
            top: 1.5rem;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
        }

        .tiny-search input {
            max-width: 220px !important;
            height: 30px !important;
            font-size: 0.8rem !important;
            padding: 0.2rem 0.5rem !important;
        }
    </style>
""", unsafe_allow_html=True)

# Cache the model and client to avoid reloading
@st.cache_resource
def load_model():
    from vectorize import get_embedding
    return get_embedding

@st.cache_resource
def load_qdrant_client():
    return get_client()

get_embedding = load_model()
client = load_qdrant_client()

# Search function
def search_products(query: str, collection: str, top_k: int):
    if not query.strip():
        st.warning("Please enter a search query")
        return []
    
    try:
        vector = get_embedding(query)
        try:
            results = client.search(
                collection_name=collection,
                query_vector=vector,
                limit=top_k
            )
        except:
            results = client.query_points(
                collection_name=collection,
                query=vector,
                limit=top_k
            ).points
        
        return results
    except Exception as e:
        st.error(f"Search error: {str(e)}")
        return []


def load_all_products(collection: str) -> list[dict]:
    if collection == "nike_shoes":
        df = pd.read_csv("data/nike_shoes.csv")
    elif collection == "clothing":
        df = pd.read_parquet("data/clothing.parquet")
        df = df.rename(columns={"title": "name", "subtitle": "description"})
    else:
        df = pd.read_csv("data/watches.csv")

    df = df[["name", "description", "price", "category"]].dropna()
    return [normalize_payload(row) for _, row in df.iterrows()]


def assistant_reply(user_text: str, collection: str) -> str:
    query = user_text.strip()
    if not query:
        return "Ask me about products, prices, or categories."

    results = search_products(query, collection, top_k=3)
    if not results:
        return "I couldn't find matching products. Try a different description."

    lines = []
    for hit in results:
        payload = hit.payload if hasattr(hit, "payload") else hit
        name = payload.get("name", "N/A")
        price = payload.get("price", 0)
        category = payload.get("category", "N/A")
        lines.append(f"• {name} — ${price:.2f} ({category})")

    return "Here are a few good matches:\n" + "\n".join(lines)


# ===== MAIN LAYOUT =====
# Header (minimal, professional)
header_left, header_right = st.columns([4, 1])
with header_left:
    st.markdown('<p class="main-header">ArbitrageAI</p>', unsafe_allow_html=True)
    st.markdown('<p class="subheader">Product discovery + AR preview</p>', unsafe_allow_html=True)
with header_right:
    st.markdown("<div class='tiny-search'>", unsafe_allow_html=True)
    search_query = st.text_input("", placeholder="Search", label_visibility="collapsed", key="search_query_top")
    st.markdown("</div>", unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.markdown("## ⚙️ Search Settings")
    st.divider()
    
    st.markdown("#### Filters")
    
    collection = st.radio(
        "📦 Collection",
        ["clothing", "nike_shoes"],
        format_func=lambda x: f"👟 Clothing" if x == "clothing" else "👟 Nike Shoes"
    )
    
    top_k = st.slider(
        "📊 Results to Display",
        min_value=1,
        max_value=10,
        value=5,
        help="Number of products to show"
    )

    show_grid_ar = st.toggle(
        "Show AR preview in grid",
        value=False,
        help="Embed a small 3D viewer in each product tile"
    )
    
    st.divider()
    st.markdown("### 📋 Available Products")
    
    with st.expander("👟 Clothing Items"):
        st.markdown("""
        - Nike Air Max
        - Adidas Ultraboost
        - Puma RS-X
        """)
    
    with st.expander("👟 Nike Shoes"):
        st.markdown("""
        - Nike Air Max 90 Essentials
        - Nike Air Jordan 1 Retro
        - Nike Dunk Low
        - Nike Air Force 1
        - Nike React Infinity
        - Nike SB Dunk Low Pro
        - Nike Blazer Mid
        - Nike Air Zoom Pegasus
        - Nike LeBron James XX
        - Nike Revolution 7
        """)
    
    st.divider()
    st.markdown("### 💡 Tips")
    st.info("💬 Use natural language like 'premium running shoes' or 'luxury timepiece'")

# ===== MAIN CONTENT =====
main_col, side_col = st.columns([3, 1], gap="large")

with side_col:
    st.markdown('<div class="assistant-card floating">', unsafe_allow_html=True)
    st.markdown('<div class="assistant-hint">Ask for recommendations, prices, or categories.</div>', unsafe_allow_html=True)

    if "assistant_chat" not in st.session_state:
        st.session_state.assistant_chat = []

    for msg in st.session_state.assistant_chat[-6:]:
        role = msg.get("role")
        content = msg.get("content")
        if role == "user":
            st.markdown(f'<div class="chat-bubble-user">{content}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bubble-assistant">{content}</div>', unsafe_allow_html=True)

    user_prompt = st.text_input("", placeholder="Ask the assistant…", key="assistant_input")
    if st.button("Send", use_container_width=True):
        if user_prompt.strip():
            st.session_state.assistant_chat.append({"role": "user", "content": user_prompt.strip()})
            reply = assistant_reply(user_prompt, collection)
            st.session_state.assistant_chat.append({"role": "assistant", "content": reply})
            st.experimental_rerun()

    st.markdown('</div>', unsafe_allow_html=True)

with main_col:
    if search_query:
        st.markdown(f'<p class="main-header" style="font-size: 2rem;">Search Results for "{search_query}"</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="subheader">Collection: **{collection.upper()}** | Top {top_k} Results</p>', unsafe_allow_html=True)
        
        results = search_products(search_query, collection, top_k)
        
        if results:
            for idx, result in enumerate(results, 1):
                payload = result.payload if hasattr(result, 'payload') else result
                
                with st.container():
                    st.markdown('<div class="product-card">', unsafe_allow_html=True)
                    
                    # Product Header
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.markdown(f'<p class="product-name">#{idx} {payload.get("name", "N/A")}</p>', unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f'<p class="price-tag">${payload.get("price", 0):.2f}</p>', unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f'<span class="category-badge">{payload.get("category", "N/A").upper()}</span>', unsafe_allow_html=True)
                    
                    st.markdown(f"**Description:** {payload.get('description', 'N/A')}")
                    
                    # AR Viewer Section
                    ar_model_glb = payload.get("ar_model_glb")
                    
                    if ar_model_glb:
                        st.markdown("---")
                        st.markdown("### 📱 3D AR Model Viewer")

                        viewer_html = f"""
<!DOCTYPE html>
<html lang=\"en\">
    <head>
        <meta charset=\"UTF-8\" />
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
        <script type=\"module\" src=\"https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js\"></script>
        <style>
            body {{ margin: 0; background: transparent; }}
            model-viewer {{ width: 100%; height: 500px; background: #0b1220; border-radius: 8px; }}
        </style>
    </head>
    <body>
        <model-viewer
            src=\"{ar_model_glb}\"
            alt=\"3D product model\"
            ar
            ar-modes=\"scene-viewer webxr quick-look\"
            camera-controls
            auto-rotate
            shadow-intensity=\"0.8\"
            exposure=\"1\"
        ></model-viewer>
    </body>
</html>
"""

                        html(viewer_html, height=520)
                        
                        st.markdown(f'<p class="ar-ready-badge">✅ AR Ready - Tap AR button on mobile to view in your space!</p>', unsafe_allow_html=True)
                    else:
                        st.warning("⚠️ AR model not available for this product yet")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown("")
        else:
            st.error(f"❌ No products found matching '{search_query}'. Try a different search term!")

    st.markdown("---")
    st.markdown('<p class="main-header" style="font-size: 2rem;">All Products</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="subheader">Collection: **{collection.upper()}**</p>', unsafe_allow_html=True)

    all_products = load_all_products(collection)
    if all_products:
        st.markdown('<div class="product-row">', unsafe_allow_html=True)
        for payload in all_products:
            ar_model_glb = payload.get("ar_model_glb")
            st.markdown(
                f"""
                <div class=\"product-tile\">
                    <div class=\"product-name\">{payload.get('name', 'N/A')}</div>
                    <div class=\"price-tag\">${payload.get('price', 0):.2f}</div>
                    <div style=\"margin: 0.5rem 0;\"><span class=\"category-badge\">{payload.get('category', 'N/A').upper()}</span></div>
                    <div style=\"color: #475569; font-size: 0.9rem;\">{payload.get('description', 'N/A')}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            if show_grid_ar and ar_model_glb:
                viewer_html_small = f"""
<!DOCTYPE html>
<html lang=\"en\">
    <head>
        <meta charset=\"UTF-8\" />
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
        <script type=\"module\" src=\"https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js\"></script>
        <style>
            body {{ margin: 0; background: transparent; }}
            model-viewer {{ width: 100%; height: 220px; background: #0b1220; border-radius: 10px; }}
        </style>
    </head>
    <body>
        <model-viewer
            src=\"{ar_model_glb}\"
            alt=\"3D product model\"
            ar
            ar-modes=\"scene-viewer webxr quick-look\"
            camera-controls
            auto-rotate
            shadow-intensity=\"0.6\"
            exposure=\"1\"
        ></model-viewer>
    </body>
</html>
"""
                html(viewer_html_small, height=230)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("No products found in this collection.")

# Footer
st.markdown("""
    <div class="footer">
        <p>🚀 <strong>ArbitrageAI</strong> © 2026</p>
        <p>Powered by Qdrant + Sentence-Transformers + Streamlit</p>
        <p>Semantic Search meets Augmented Reality</p>
    </div>
""", unsafe_allow_html=True)
