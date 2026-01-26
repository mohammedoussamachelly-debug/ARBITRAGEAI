
from sentence_transformers import SentenceTransformer

class ProductVectorizer:
    def __init__(self, model=None, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize the embedding model. You can pass a preloaded model or a model name.
        """
        self.model = model or SentenceTransformer(model_name)

    def encode_visual(self, description: str) -> list:
        """
        Generate a visual embedding from a product description.
        """
        if not description or not isinstance(description, str):
            raise ValueError("Product description must be a non-empty string.")
        return self.model.encode(description).tolist()

    def build_payload(self, name: str, market_data: dict) -> dict:
        """
        Combine product name and market metadata into a payload.
        """
        if not name or not isinstance(name, str):
            raise ValueError("Product name must be a non-empty string.")
        if not isinstance(market_data, dict):
            raise ValueError("Market data must be a dictionary.")
        return {
            "name": name,
            **market_data
        }

    def vectorize_product(self, product: dict) -> tuple:
        """
        Given a product dict with 'name', 'visual_description', and 'market_payload',
        return (vector, payload) tuple.
        """
        required_keys = {"name", "visual_description", "market_payload"}
        if not required_keys.issubset(product.keys()):
            raise KeyError(f"Product must contain keys: {required_keys}")

        vector = self.encode_visual(product["visual_description"])
        payload = self.build_payload(product["name"], product["market_payload"])
        return vector, payload
