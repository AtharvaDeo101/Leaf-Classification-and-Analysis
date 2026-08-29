from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import text

from backend.app.db import engine
from backend.app.services.registry import registry
from src.cv.pipeline import PIPELINE_VERSION

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False
    return {
        "status": "ok" if db_ok else "degraded",
        "database": db_ok,
        "pipeline_version": PIPELINE_VERSION,
        "default_model": registry.default_key,
        "models_loaded": sum(1 for m in registry.describe() if m["loaded"]),
    }