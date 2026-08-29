
from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
from loguru import logger

from backend.app.config import settings
from src.cv.pipeline import to_vector
#sequence of selecting the models - hybrid - svm - random forest
CLASSICAL_FILES = {
    "svm": "svm_bundle.joblib",
    "random_forest": "rf_bundle.joblib",
    "hybrid": "hybrid_bundle.joblib",
}


class LoadedModel:
    def __init__(self, key: str, kind: str, bundle: dict):
        self.key = key
        self.kind = kind
        self.model = bundle["model"]
        self.scaler = bundle.get("scaler")
        self.feature_names: list[str] = list(bundle["feature_names"])
        self.classes: list[str] = [str(c) for c in bundle["classes"]]
        self.metrics: dict = bundle.get("metrics", {})
        # Absent in bundles trained before the novelty guard existed.
        self.novelty: dict | None = bundle.get("novelty")

    def novelty_distance(self, features: dict) -> float | None:
        """Distance to the nearest reference leaf, or None if unguarded.

        Carries its own scaler: the random-forest bundle has scaler=None, but
        the guard is always measured in the same standardised space.
        """
        if self.novelty is None:
            return None
        x = to_vector(features, self.feature_names)
        x = self.novelty["scaler"].transform(x)
        return float(self.novelty["nn"].kneighbors(x, n_neighbors=1)[0][0, 0])

    def is_off_collection(self, features: dict) -> tuple[bool, float | None]:
        distance = self.novelty_distance(features)
        if distance is None:
            return False, None
        return distance > float(self.novelty["threshold"]), distance

    def predict(self, features: dict, top_k: int = 5) -> list[dict]:
        x = to_vector(features, self.feature_names)
        if self.scaler is not None:
            x = self.scaler.transform(x)

        if hasattr(self.model, "predict_proba"):
            probs = np.asarray(self.model.predict_proba(x))[0]
        elif hasattr(self.model, "decision_function"):
            scores = np.atleast_2d(self.model.decision_function(x))[0]
            exp = np.exp(scores - scores.max())
            probs = exp / exp.sum()
        else:
            idx = int(self.model.predict(x)[0])
            probs = np.zeros(len(self.classes))
            probs[idx] = 1.0

        order = np.argsort(probs)[::-1][:top_k]
        return [{"label": self.classes[i], "confidence": float(probs[i])}
                for i in order]


class Registry:
    def __init__(self) -> None:
        self._models: dict[str, LoadedModel] = {}
        self._default: str | None = None

    def load_all(self) -> None:
        root: Path = settings.artifacts_dir
        for key, fname in CLASSICAL_FILES.items():
            path = root / fname
            if not path.exists():
                logger.info(f"Model artifact not found, skipping: {fname}")
                continue
            try:
                bundle = joblib.load(path)
                self._models[key] = LoadedModel(key, "classical", bundle)
                logger.success(f"Loaded model '{key}' "
                               f"({len(self._models[key].classes)} classes)")
            except Exception as exc:
                logger.error(f"Failed to load {fname}: {exc}")

        for preferred in ("hybrid", "svm", "random_forest"):
            if preferred in self._models:
                self._default = preferred
                break
        if self._default is None:
            logger.warning("No models loaded. /analyze will return features only.")

    def get(self, key: str | None) -> LoadedModel | None:
        if key:
            return self._models.get(key)
        return self._models.get(self._default) if self._default else None

    def describe(self) -> list[dict]:
        out = [{"key": k, "kind": m.kind, "loaded": True,
                "n_classes": len(m.classes),
                "n_features": len(m.feature_names), "metrics": m.metrics}
               for k, m in self._models.items()]
        for k in CLASSICAL_FILES:
            if k not in self._models:
                out.append({"key": k, "kind": "classical", "loaded": False,
                            "n_classes": None, "n_features": None, "metrics": {}})
        return out

    @property
    def default_key(self) -> str | None:
        return self._default


registry = Registry()