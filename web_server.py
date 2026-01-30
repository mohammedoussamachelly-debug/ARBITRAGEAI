from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Allow importing from ./src
ROOT = Path(__file__).resolve().parent
sys.path.append(str(ROOT / "src"))

from qdrant_utils import get_client  # noqa: E402


app = FastAPI(title="ArbitrageAI Web")

WEB_DIR = ROOT / "web"
MODELS_DIR = ROOT / "web_models"

# Serve frontend assets without shadowing API routes.
app.mount("/assets", StaticFiles(directory=str(WEB_DIR / "assets")), name="assets")


@app.get("/")
def index():
    index_path = WEB_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="index.html not found")
    return FileResponse(str(index_path))


def _get_embedding_func():
    from vectorize import get_embedding  # local import to avoid slow import at startup

    return get_embedding


def _normalize_ar_url(request: Request, payload: dict[str, Any]) -> dict[str, Any]:
    # Always point Nike results to our own hosted model to avoid CORS/mixed-content.
    name = str(payload.get("name", "")).lower()
    if "nike" in name:
        payload["ar_model_glb"] = str(request.base_url).rstrip("/") + "/models/nike_air_max.glb"
    return payload


@app.get("/models/nike_air_max.glb")
def get_nike_model():
    model_path = MODELS_DIR / "nike_air_max.glb"
    if not model_path.exists():
        raise HTTPException(status_code=404, detail="Model file not found")

    return FileResponse(
        str(model_path),
        filename="nike_air_max.glb",
        media_type="model/gltf-binary",
    )


@app.get("/api/search")
def api_search(
    request: Request,
    q: str = Query(..., min_length=1),
    collection: str = Query("nike_shoes"),
    top_k: int = Query(5, ge=1, le=20),
):
    query = q.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Empty query")

    try:
        client = get_client()
        get_embedding = _get_embedding_func()
        vector = get_embedding(query)

        # qdrant-client 1.16+ removed search(); use query_points().
        if hasattr(client, "search"):
            results = client.search(collection_name=collection, query_vector=vector, limit=top_k)
        else:
            results = client.query_points(
                collection_name=collection,
                query=vector,
                limit=top_k,
                with_payload=True,
            ).points
        payloads: list[dict[str, Any]] = []

        for r in results:
            payload = dict(getattr(r, "payload", {}) or {})
            payload = _normalize_ar_url(request, payload)
            payloads.append(payload)

        return {"results": payloads}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", "8080"))
    uvicorn.run("web_server:app", host="0.0.0.0", port=port, reload=True)
