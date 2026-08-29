from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class Prediction(BaseModel):
    label: str
    confidence: float = Field(ge=0.0, le=1.0)


class FeatureGroups(BaseModel):
    geometric: dict[str, float] = {}
    moments: dict[str, float] = {}
    contour: dict[str, float] = {}
    margin: dict[str, float] = {}
    veins: dict[str, float] = {}
    texture: dict[str, float] = {}
    color: dict[str, float] = {}


class AnalysisResult(BaseModel):
    id: str
    filename: str
    created_at: datetime
    model_key: str | None = None
    prediction: Prediction | None = None
    top_k: list[Prediction] = []
    margin_type: str | None = None
    feature_groups: FeatureGroups
    feature_count: int
    meta: dict = {}
    stage_urls: dict[str, str] = {}


class SegmentResult(BaseModel):
    id: str
    stage_urls: dict[str, str]
    meta: dict


class HistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    filename: str
    predicted_label: str | None
    confidence: float | None
    margin_type: str | None


class HistoryPage(BaseModel):
    total: int
    items: list[HistoryItem]


class ModelInfo(BaseModel):
    key: str
    kind: str
    loaded: bool
    n_classes: int | None = None
    n_features: int | None = None
    metrics: dict = {}


class Species(BaseModel):
    id: str
    common_name: str
    scientific_name: str
    family: str | None = None
    margin_type: str | None = None
    notes: str | None = None