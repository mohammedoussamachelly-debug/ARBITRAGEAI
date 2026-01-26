from sentence_transformers import SentenceTransformer

# Load the MiniLM model once
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text: str):
    """
    Generate a single embedding for a given text string.
    """
    return model.encode(text).tolist()

def get_embeddings(texts: list[str]):
    """
    Generate embeddings for a list of text strings.
    """
    return model.encode(texts).tolist()
