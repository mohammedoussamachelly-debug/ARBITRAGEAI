import streamlit as st
import sys
sys.path.append('src')

from qdrant_utils import get_client
from qdrant_client.models import Filter, FieldCondition, MatchValue
import pandas as pd
from streamlit.components.v1 import html

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
        # Use search() API which returns ScoredPoint with full payload
        try:
            results = client.search(
                collection_name=collection,
                query_vector=vector,
                limit=top_k
            )
        except:
            # Fallback to query_points for older API versions
            results = client.query_points(
                collection_name=collection,
                query=vector,
                limit=top_k
            ).points
        
        # Debug: print first result payload to verify AR model field
        if results:
            st.write("DEBUG: First result payload:", results[0].payload if hasattr(results[0], 'payload') else results[0])
        
        return results
    except Exception as e:
        st.error(f"Search error: {str(e)}")
        return []


# Sidebar inputs
st.sidebar.header("🔎 Product Search")
search_query = st.sidebar.text_input("Enter your search query:")
collection = st.sidebar.selectbox("Select collection:", ["clothing", "watches"], index=0)
top_k = st.sidebar.slider("Number of results", min_value=1, max_value=10, value=5)

# Perform search if query exists
if search_query:
    st.markdown(f"### Search Results for: **{search_query}** in {collection}")
    results = search_products(search_query, collection, top_k)
    if results:
        # Display results in columns
        cols = st.columns(min(3, len(results)))
        for idx, result in enumerate(results):
            # Handle both ScoredPoint and PointStruct responses
            payload = result.payload if hasattr(result, 'payload') else result
            col = cols[idx % 3]
            with col:
                st.markdown(f"#### {payload.get('name', 'N/A')}")
                # Display product details
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Price", f"${payload.get('price', 0):.2f}")
                with col2:
                    st.metric("Category", payload.get('category', 'N/A').title())
                st.markdown(f"**Description:** {payload.get('description', 'N/A')}")
                # AR Button - Direct model viewer
                ar_model_glb = payload.get("ar_model_glb")
                ar_model_usdz = payload.get("ar_model_usdz")
                if ar_model_glb:
                    # Handle both direct GLB URLs and HTML viewer URLs
                    if ar_model_glb.endswith('.html') or 'viewer.html' in ar_model_glb:
                        # Direct HTML viewer URL
                        viewer_url = ar_model_glb
                    else:
                        # GLB file - use modelviewer.dev
                        viewer_url = f"https://modelviewer.dev/?url={ar_model_glb}&ar=true&autoplay=true&camera-controls=true"
                    
                    st.markdown(
                        f"""
                        <iframe 
                            style="width:100%; height:500px; border:none; border-radius:8px;"
                            src="{viewer_url}">
                        </iframe>
                        """,
                        unsafe_allow_html=True
                    )
                    st.info("📱 **AR Ready!** Open on mobile and tap the AR icon to see it in your space")
                else:
                    st.info("❌ AR model not available for this product")
                st.divider()
    else:
        st.info("No results found. Try a different search term.")
else:
    st.info("👈 Enter a search query in the sidebar to get started!")
    # Show available collections
    st.markdown("### 📦 Available Collections")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**👟 Clothing**")
        st.markdown("- Nike Air Max")
        st.markdown("- Adidas Ultraboost")
        st.markdown("- Puma RS-X")
    with col2:
        st.markdown("**⌚ Watches**")
        st.markdown("- Rolex Submariner")
        st.markdown("- Omega Seamaster")
        st.markdown("- Breitling Navitimer")

# Footer
st.markdown("---")
st.markdown("**ArbitrageAI** © 2026 | Powered by Qdrant + Sentence-Transformers")
