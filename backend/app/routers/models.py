from __future__ import annotations

from fastapi import APIRouter

from backend.app.schemas import ModelInfo
from backend.app.services.registry import registry

router = APIRouter(prefix="/api", tags=["models"])


@router.get("/models", response_model=list[ModelInfo])
def list_models():
    return registry.describe()


@router.post("/models/reload")
def reload_models():
    """Reload artifacts without restarting — handy while iterating on training."""
    registry.load_all()
    return {"default": registry.default_key, "models": registry.describe()}