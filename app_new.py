import streamlit as st
import sys
sys.path.append('src')

from qdrant_utils import get_client
from qdrant_client.models import Filter, FieldCondition, MatchValue
import pandas as pd
from streamlit.components.v1 import html

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
            --primary-color: #6366f1;
            --secondary-color: #ec4899;
            --success-color: #10b981;
            --warning-color: #f59e0b;
            --danger-color: #ef4444;
            --dark-bg: #0f172a;
            --light-bg: #f8fafc;
        }
        
        .main-header {
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #6366f1 0%, #ec4899 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        
        .subheader {
            color: #64748b;
            font-size: 1.1rem;
            margin-bottom: 2rem;
        }
        
        .product-card {
            border-radius: 12px;
            padding: 1.5rem;
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(236, 72, 153, 0.05) 100%);
            border: 1px solid rgba(99, 102, 241, 0.1);
            transition: all 0.3s ease;
            margin-bottom: 1rem;
        }
        
        .product-card:hover {
            border: 1px solid rgba(99, 102, 241, 0.3);
            box-shadow: 0 4px 20px rgba(99, 102, 241, 0.1);
        }
        
        .product-name {
            font-size: 1.3rem;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 0.5rem;
        }
        
        .product-meta {
            display: flex;
            gap: 1rem;
            margin: 0.75rem 0;
            font-size: 0.9rem;
        }
        
        .price-tag {
            font-size: 1.5rem;
            font-weight: 800;
            color: #10b981;
        }
        
        .category-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            background-color: rgba(99, 102, 241, 0.1);
            color: #6366f1;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }
        
        .ar-ready-badge {
            display: inline-block;
            padding: 0.5rem 1rem;
            background-color: rgba(16, 185, 129, 0.1);
            color: #10b981;
            border-radius: 8px;
            font-weight: 600;
            margin-top: 0.5rem;
        }
        
        .search-container {
            background: linear-gradient(135deg, #6366f1 0%, #ec4899 100%);
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            color: white;
        }
        
        .collection-item {
            padding: 1rem;
            border-radius: 8px;
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(236, 72, 153, 0.1) 100%);
            margin-bottom: 0.5rem;
            border-left: 3px solid #6366f1;
        }
        
        .footer {
            text-align: center;
            padding: 2rem;
            color: #94a3b8;
            font-size: 0.9rem;
            border-top: 1px solid #e2e8f0;
            margin-top: 3rem;
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


# ===== MAIN LAYOUT =====
# Header
st.markdown('<p class="main-header">🚀 ArbitrageAI</p>', unsafe_allow_html=True)
st.markdown('<p class="subheader">Semantic Search + Augmented Reality Product Viewer</p>', unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.markdown("## ⚙️ Search Settings")
    st.divider()
    
    search_query = st.text_input(
        "🔍 Search Products",
        placeholder="E.g., Nike shoes, luxury watch...",
        help="Enter a product description or name"
    )
    
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
else:
    # Welcome Screen
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("## 🎯 How It Works")
        st.markdown("""
        1. **Search** - Enter what you're looking for
        2. **Explore** - View products with detailed info
        3. **View AR** - See the product in 3D on your phone
        4. **Experience** - Use AR to visualize in your space
        """)
    
    with col2:
        st.markdown("## 🌟 Features")
        st.markdown("""
        ✨ **Semantic Search** - Find products by description
        
        🎯 **AI-Powered** - Intelligent product matching
        
        📱 **AR Ready** - Augmented Reality for mobile
        
        ⚡ **Fast Search** - Powered by Qdrant Vector DB
        """)

# Footer
st.markdown("""
    <div class="footer">
        <p>🚀 <strong>ArbitrageAI</strong> © 2026</p>
        <p>Powered by Qdrant + Sentence-Transformers + Streamlit</p>
        <p>Semantic Search meets Augmented Reality</p>
    </div>
""", unsafe_allow_html=True)
