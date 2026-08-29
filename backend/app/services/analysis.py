from __future__ import annotations

import uuid

from loguru import logger
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.db_models import Analysis
from backend.app.services import storage
from backend.app.services.registry import registry
from src.cv.pipeline import analyse

GROUP_PREFIXES = {
    "geometric": ("geo_",),
    "moments": ("hu_", "zernike_"),
    "contour": ("efd_", "ccd_"),
    "margin": ("margin_",),
    "veins": ("vein_",),
    "texture": ("glcm_", "lbp_"),
    "color": ("color_",),
}


def group_features(features: dict[str, float]) -> dict[str, dict[str, float]]:
    grouped = {g: {} for g in GROUP_PREFIXES}
    for name, value in features.items():
        for group, prefixes in GROUP_PREFIXES.items():
            if name.startswith(prefixes):
                grouped[group][name] = value
                break
    return grouped


def run_analysis(db: Session, raw: bytes, filename: str,
                 model_key: str | None = None, top_k: int = 5,
                 with_stages: bool = True) -> Analysis:
    analysis_id = uuid.uuid4().hex

    result = analyse(raw, work_size=settings.work_size, want_stages=with_stages)
    features = result["features"]
    meta = result["meta"]

    stage_urls: dict[str, str] = {}
    if with_stages:
        stage_urls = storage.save_stages(analysis_id, result["stages"])
    stage_urls["upload"] = storage.save_upload(analysis_id, raw, filename)

    predictions: list[dict] = []
    model = registry.get(model_key)
    if model is not None:
        try:
            predictions = model.predict(features, top_k=top_k)
        except Exception as exc:
            logger.error(f"Inference failed for {analysis_id}: {exc}")

    record = Analysis(
        id=analysis_id,
        filename=filename,
        model_key=model.key if model else None,
        predicted_label=predictions[0]["label"] if predictions else None,
        confidence=predictions[0]["confidence"] if predictions else None,
        margin_type=meta.get("margin_type"),
        features=features,
        top_k=predictions,
        meta=meta,
        stage_urls=stage_urls,
    )
    db.add(record)
    db.commit()
    return record


def to_result_dict(record: Analysis) -> dict:
    top_k = record.top_k or []
    return {
        "id": record.id,
        "filename": record.filename,
        "created_at": record.created_at,
        "model_key": record.model_key,
        "prediction": top_k[0] if top_k else None,
        "top_k": top_k,
        "margin_type": record.margin_type,
        "feature_groups": group_features(record.features or {}),
        "feature_count": len(record.features or {}),
        "meta": record.meta or {},
        "stage_urls": record.stage_urls or {},
    }