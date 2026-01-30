import socket


def _get_local_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def normalize_payload(row: dict) -> dict:
    """
    Normalize product data and add AR model URLs for supported products.
    """
    product_name = str(row["name"]).strip().lower()

    # Match model manually
    ar_model_glb = None
    
    # Nike Air Max models - serve via local server to avoid CORS issues
    if "nike air max 90" in product_name or "air max 90" in product_name:
        # Serve via local server. Automatically detect LAN IP.
        ip = _get_local_ip()
        ar_model_glb = f"http://{ip}:9000/nike_air_max.glb"
    elif "nike" in product_name:
        # Fallback for other Nike products to use the Air Max model
        ip = _get_local_ip()
        ar_model_glb = f"http://{ip}:9000/nike_air_max.glb"
    # Add more products here as you add more models
    # elif "adidas" in product_name:
    #     ar_model_glb = "https://..."
    # elif "rolex" in product_name:
    #     ar_model_glb = "https://..."

    return {
        "name": row["name"],
        "description": row["description"],
        "price": row["price"],
        "category": row["category"],
        "ar_model_glb": ar_model_glb,
        "ar_model_usdz": None  # Add later if you convert to .usdz
    }
