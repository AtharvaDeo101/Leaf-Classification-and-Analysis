
from __future__ import annotations

import cv2
import numpy as np

from src.cv import preprocessing, segmentation
from src.cv.features import color, fourier, geometric, margin, moments, texture, veins

PIPELINE_VERSION = "1.0.0"


def analyse(raw: bytes, work_size: int = 800, want_stages: bool = True) -> dict:
    pre = preprocessing.preprocess(raw, work_size=work_size)
    work = pre["preprocessed"]

    seg = segmentation.segment(work)
    pet = segmentation.remove_petiole(seg["mask"])
    norm = segmentation.normalise_orientation(pet["mask"], work)

    mask, bgr = norm["mask"], norm["bgr"]
    contour = segmentation.main_contour(mask)

    features: dict[str, float] = {}
    features.update(geometric.extract(contour, mask))
    features.update(moments.extract(contour, mask))
    features.update(fourier.extract(contour))
    margin_feats = margin.extract(contour)
    features.update(margin_feats)
    features.update(veins.extract(bgr, mask))
    features.update(texture.extract(bgr, mask))
    features.update(color.extract(bgr, mask))

    meta = {k[1:]: v for k, v in features.items() if k.startswith("_")}
    features = {k: v for k, v in features.items() if not k.startswith("_")}
    features = {k: (0.0 if not np.isfinite(v) else float(v))
                for k, v in features.items()}

    result = {
        "pipeline_version": PIPELINE_VERSION,
        "features": features,
        "meta": {
            **meta,
            "segmentation_method": seg["method"],
            "petiole_removed": pet["removed"],
            "rotation_angle": round(norm["angle"], 2),
            "original_shape": list(pre["original_shape"]),
            "work_shape": list(pre["work_shape"]),
            "n_features": len(features),
        },
    }
    if want_stages:
        result["stages"] = _render_stages(pre["resized"], seg["mask"], mask,
                                          bgr, contour)
    return result


def _render_stages(resized, raw_mask, final_mask, rotated_bgr, contour) -> dict:
    """Stage images for the frontend pipeline viewer. Keys become filenames."""
    overlay = rotated_bgr.copy()
    cv2.drawContours(overlay, [contour], -1, (0, 0, 255), 2)

    hull = cv2.convexHull(contour)
    cv2.drawContours(overlay, [hull], -1, (255, 128, 0), 1)
    if len(contour) >= 5:
        cv2.ellipse(overlay, cv2.fitEllipse(contour), (0, 200, 0), 1)

    try:
        hull_idx = np.sort(cv2.convexHull(contour, returnPoints=False)
                           .flatten())[::-1].reshape(-1, 1)
        defects = cv2.convexityDefects(contour, hull_idx)
        if defects is not None:
            eq_d = np.sqrt(4 * cv2.contourArea(contour) / np.pi)
            for s, e, f, d in defects[:, 0]:
                if d / 256.0 > 0.02 * eq_d:
                    cv2.circle(overlay, tuple(contour[f][0]), 4, (0, 255, 255), -1)
    except cv2.error:
        pass

    return {
        "original": resized,
        "mask_raw": cv2.cvtColor(raw_mask, cv2.COLOR_GRAY2BGR),
        "mask_final": cv2.cvtColor(final_mask, cv2.COLOR_GRAY2BGR),
        "descriptors": overlay,
    }


def feature_names(sample_raw: bytes, work_size: int = 800) -> list[str]:
    """Canonical ordered feature names — persist this alongside the model."""
    return sorted(analyse(sample_raw, work_size, want_stages=False)["features"])


def to_vector(features: dict, names: list[str]) -> np.ndarray:
    """Reorder a feature dict into the exact column order the model was fit on.

    Reordering by saved names rather than by dict insertion is what stops a
    silent accuracy collapse when the pipeline gains a new descriptor.
    """
    return np.array([[float(features.get(n, 0.0)) for n in names]], dtype=np.float64)