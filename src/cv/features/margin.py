
from __future__ import annotations

import cv2
import numpy as np

EPS = 1e-9


def extract(contour: np.ndarray) -> dict:
    area = float(cv2.contourArea(contour))
    perimeter = float(cv2.arcLength(contour, True))
    eq_diameter = float(np.sqrt(4.0 * area / np.pi)) + EPS

    depths: np.ndarray
    try:
        hull_idx = cv2.convexHull(contour, returnPoints=False)
        hull_idx = np.sort(hull_idx.flatten())[::-1].reshape(-1, 1)
        defects = cv2.convexityDefects(contour, hull_idx)
        depths = (defects[:, 0, 3] / 256.0) if defects is not None else np.array([])
    except cv2.error:
        depths = np.array([])

    # Anything shallower than 2% of the equivalent diameter is contour noise.
    threshold = 0.02 * eq_diameter
    significant = depths[depths > threshold] / eq_diameter

    n_teeth = int(significant.size)
    mean_depth = float(significant.mean()) if n_teeth else 0.0
    max_depth = float(significant.max()) if n_teeth else 0.0
    std_depth = float(significant.std()) if n_teeth else 0.0
    tooth_density = n_teeth / (perimeter / eq_diameter + EPS)

    if n_teeth == 0 or max_depth < 0.03:
        margin_type = "entire"
    elif max_depth > 0.25 and n_teeth <= 12:
        margin_type = "lobed"
    elif mean_depth > 0.08:
        margin_type = "dentate"
    else:
        margin_type = "serrate"

    return {
        "margin_n_teeth": float(n_teeth),
        "margin_mean_depth": mean_depth,
        "margin_max_depth": max_depth,
        "margin_std_depth": std_depth,
        "margin_tooth_density": float(tooth_density),
        "margin_lobedness": float(mean_depth * n_teeth),
        "_margin_type": margin_type,  # underscore keys are metadata, not features
    }