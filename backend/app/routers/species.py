from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, HTTPException

from backend.app.schemas import Species

router = APIRouter(prefix="/api", tags=["species"])
DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "species.json"


@lru_cache(maxsize=1)
def _load() -> dict[str, dict]:
    if not DATA_FILE.exists():
        return {}
    records = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return {r["id"]: r for r in records}


@router.get("/species", response_model=list[Species])
def list_species():
    return list(_load().values())


@router.get("/species/{species_id}", response_model=Species)
def get_species(species_id: str):
    record = _load().get(species_id)
    if record is None:
        raise HTTPException(404, "Species not found.")
    return record